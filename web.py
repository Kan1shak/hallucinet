import re
from llms import LLMWrapper, CreativeWriter, JSONWriter
from prompts import *

class SearchEngine:
    def __init__(self, llm_provider_type, **llm_provider_kwargs):
        self.creative_writer = CreativeWriter(search_creative_system_prompt, llm_provider_type, **llm_provider_kwargs)
        self.json_writer = JSONWriter(search_json_system_prompt, SearchResults, llm_provider_type, **llm_provider_kwargs)

    def search(self, query, max_results=7):
        query_with_max_results = f"Query:{query}\nMax Results to Return:{max_results}"
        results_plain_text =  self.creative_writer.creative_loop(query_with_max_results)
        print(results_plain_text)
        match = re.search(r"<search_results>(.*?)</search_results>", results_plain_text, re.DOTALL)
        if match:
            results_plain_text = match.group(1).strip()
        else:
            raise ValueError(f"Error with extracting the xml tag from the results. Results:\n{results_plain_text}")

        
        return self.json_writer.convertToJSON(f"# Query: {query}\n# max_results: {max_results}\n\n{results_plain_text}")
    
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