import re, queue
from llms import LLMWrapper, CreativeWriter, JSONWriter
from prompts import *

class SearchEngine:
    def __init__(self, llm_provider_type, **llm_provider_kwargs):
        self.creative_writer = CreativeWriter(hallucinations_plus_plus_creative_system_prompt, llm_provider_type, **llm_provider_kwargs)
        self.json_writer = JSONWriter(search_json_system_prompt, SearchResults, llm_provider_type, **llm_provider_kwargs)
        self.progress_queue = queue.Queue()

    def search(self, query, max_results=7):
        # Send initial progress
        self.progress_queue.put({"status": "started", "message": "Checking wallet...", "progress": 0})
        
        # Creative writing phase
        self.progress_queue.put({"status": "processing", "message": "No Money", "progress": 30})
        query_with_max_results = f"Query:{query}\nMax Results to Return:{max_results}"
        results_plain_text = self.creative_writer.creative_loop(query_with_max_results)
        
        self.progress_queue.put({"status": "processing", "message": "Being unpaid sucks", "progress": 60})
        match = re.search(r"<search_results>(.*?)</search_results>", results_plain_text, re.DOTALL)
        user_metadata = re.search(r"<user_metadata>(.*?)</user_metadata>", results_plain_text, re.DOTALL)
        
        if match and user_metadata:
            results_plain_text = match.group(1).strip() + "\n" + user_metadata.group(1).strip()
        else:
            self.progress_queue.put({"status": "error", "message": "Error extracting results", "progress": 100})
            raise ValueError(f"Error with extracting the search results or metadata")

        # JSON conversion phase
        self.progress_queue.put({"status": "processing", "message": "Anyway, here are your search results...", "progress": 90})
        result = self.json_writer.convertToJSON(
            f"# Query: {query}\n# max_results: {max_results}\n\n{results_plain_text}\n- For the user metadata, summarize the key points."
        )
        
        # final completion status will be sent by the caller
        return result
    
class WebPage:
    def __init__(self, llm_provider_type, **llm_provider_kwargs):
        self.layout_maker = CreativeWriter(WebPagePrompts.sp_describe_layouts, llm_provider_type, **llm_provider_kwargs)
        self.content_maker = CreativeWriter(WebPagePrompts.sp_describe_content_for_layout, llm_provider_type, **llm_provider_kwargs)
        self.creative_writer = CreativeWriter(WebPagePrompts.sp_creative_content, llm_provider_type, **llm_provider_kwargs)
        self.html_writer = CreativeWriter(WebPagePrompts.sp_convert_to_html, llm_provider_type, **llm_provider_kwargs)
        # add a image maker later

    def get_webpage(self, url,desc,title):
        query = f"Webpage Details:\nTitle:{title}\nDescription:{desc}\nURL:{url}"
        # first make it plan a layout
        layout = self.layout_maker.creative_loop(query)
        # filling in that layout with content that might be on the page
        content = self.content_maker.creative_loop(layout)
        # itereate over the content to make it more creative
        creative_content = self.creative_writer.creative_loop(content)
        # now give it the planned layout with the final content
        final_prompt = f"""{layout}\n\n{creative_content}"""
        return self.html_writer.creative_loop(final_prompt)