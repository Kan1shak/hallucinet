# TODO: Make the bookmark button functional
# TODO: Add a settings page
# TODO: Work on reflections page

import json
import queue
import uuid
import redis
from fasthtml.common import *
from web import SearchEngine

import dotenv

dotenv.load_dotenv('.env')
GEMINI_KEY = os.getenv('GEMINI_KEY')

# a local version of the searcher
LOCAL_LLM_KEY = os.getenv('LOCAL_LLM_KEY')

searchers = {}

r = redis.Redis()

def get_or_set(domain:str, key:str, callback, **kwargs):
    if r.exists(f"{domain}:{key}"):
        return json.loads(r.get(f"{domain}:{key}"))
    else:
        value = callback(**kwargs)
        r.set(f"{domain}:{key}",json.dumps(value))
        return value

def not_found(request:Request,exc:Exception):
    # if its a htmx AJAX request, we return only the content
    if request.headers.get('HX-Request') == 'true':
        return (
            Title('404 - Not Found | HalluciNet'),
            toolbar('hallucinet.hln/404'),
            Div(
                H1('404 - Not Found', cls='title'),
                P('The page you are looking for does not exist.', cls='subtitle'),
                cls='header'
            )
        )
    else:
        return (
            Link(rel='stylesheet', href='css/homepage.css'),
            Link(rel='stylesheet', href='css/search.css'),
            Link(rel='stylesheet', href='https://fonts.googleapis.com/css2?family=BhuTuka+Expanded+One&family=JetBrains+Mono:ital,wght@0,100..800;1,100..800&display=swap'),
            Title('404 - Not Found | HalluciNet'),
            Main(
                toolbar('hallucinet.hln/404'),
                Div(
                    Div(
                        H1('404 - Not Found', cls='title'),
                        P('The page you are looking for does not exist.', cls='subtitle'),
                        cls='four-o-four'
                    ),
                    cls='content-view'
                ),
            )
        )

exception_handlers = {
    404: not_found
}

app, rt = fast_app(
    pico=False,static_path='static',
    hdrs=(Link(rel='stylesheet', href='https://www.nerdfonts.com/assets/css/webfont.css'),
        Link(rel='stylesheet', href='css/toolbar.css'),
        Link(rel='stylesheet', href='css/global.css'),
        Link(rel='preconnect', href='hhttps://fonts.googleapis.com'),
        Link(rel='preconnect', href='https://fonts.gstatic.com', crossorign=True),
        Script(src="https://unpkg.com/htmx-ext-sse@2.2.1/sse.js")
    ),
    exception_handlers=exception_handlers
)


def nav():
    nav = Ul(
        Li(A('Behind the Illusion', hx_get='/about')),
        Li(A('Reflections', hx_get='/reflections')),
        Li(A('Tune your Oracle', hx_get='/settings')),
        cls='navbar'
    )
    return Nav(nav)

def toolbar(address='hallucinet.hln'):
    toolbar = Div(
        Div(
            Div(
                Button(I(cls='nf nf-fa-angle_left'), title='Go Back', cls='navigation-button',onclick="window.history.back()"),
                Button(I(cls='nf nf-fa-angle_right'), title='Go Forward', cls='navigation-button', onclick="window.history.forward()"),
                cls='navigation-buttons',
            ),
            Div(
                Button(I(cls='nf nf-md-refresh'), title='Refresh Page', cls='navigation-button', hx_get='/refresh',
                hx_vals='js:{"url":window.location.href}'),
                Button(I(cls='nf nf-fa-home'),title='Home Page', cls='navigation-button', hx_get='/', hx_target='.content-view',hx_push_url="true"),
                cls='navigation-buttons'
            ),
            cls='navigation-buttons-container'
        ),
        Div(
            Input(type='text',value=address,placeholder='Search HalluciNet or type a HRL', cls='address-bar',
            hx_get="/resolvehrl", hx_vals='js:{"url":document.querySelector(".address-bar").value}', hx_target='.content-view', hx_push_url="true",
            hx_trigger="keyup[key=='Enter']"),
            cls='navigation-buttons address-bar-container'
        ),            
        Div(
            Button(I(cls='nf nf-md-bookmark_outline'), title='Bookamark', cls='navigation-button'),
            cls='navigation-buttons'
        ),
        cls='toolbar', id='toolbar',hx_swap_oob="true"
    )
    return toolbar

def search_bar(prefill:str=None):
    return  (

                Div(Input(type='text', placeholder='Search HalluciNet...', cls='search-bar', name='query',
                value=prefill,
                hx_get='/search', hx_target='.content-view', hx_trigger="keyup[key=='Enter']", hx_push_url="true"),
                Div(
                    Div(
                       Div(cls='progress-fill',style='width: 0%;'),
                       cls='progress-bar'
                    ),
                    Div('Starting Search...', cls='progress-message'),
                    hx_ext='sse',
                    #sse_connect='/search-progress',
                    cls='search-progress hidden',
                    id='search-progress',
                    sse_swap='progress',
                    sse_close='completed'
                ),
                Script(
                    """

document.querySelector('.search-bar').addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
        document.getElementById('search-progress').setAttribute('sse-connect','/search-progress')
        htmx.process(document.getElementById('search-progress'));
    }
});
document.querySelector('.search-bar').addEventListener('keyup', function(event) {
    if (event.key === 'Enter') {
        document.getElementById('search-progress').removeAttribute('sse-connect')
    }
});
        """),
                cls='search-bar-container'
                )
            )


def home_page():
    home_page = Div(
        Div(
            H1('HalluciNet', cls='title'),
            P('The Illusion of Reality', cls='subtitle'),
            cls='header'
        ),
        search_bar(),
        Div(
            # social links
            A('GitHub', href='https://www.github.com/Kan1shak', cls='social-link'),
            A('Twitter', href='https://www.twitter.com/unvelt', cls='social-link'),
            A('LinkedIn', href='https://www.linkedin.com/in/kanishak-sangwan-a42556154/', cls='social-link'),
            cls='social-links'
        ),
        cls='home-page'
    )
    return home_page


@app.route('/')
def index(request:Request):
    # if its a htmx AJAX request, we return only the content
    htmx_script = Script("""document.body.addEventListener('htmx:beforeRequest', function(event) {
    if (event.detail.elt.matches('input[name="query"]')) {
        document.getElementById('search-progress').classList.remove('hidden');
    }
});

document.body.addEventListener('htmx:afterRequest', function(event) {
    if (event.detail.elt.matches('input[name="query"]')) {
        document.getElementById('search-progress').classList.add('hidden');
        // close the htmx sse connection
        document.getElementById('search-progress').sse.close();
    }
});""") # idk if it even works
    if request.headers.get('HX-Request') == 'true':
        return htmx_script,toolbar(),(Title('HalluciNet'),
            nav(),
            home_page())
    else:
        return (
            Link(rel='stylesheet', href='css/homepage.css'),
            Link(rel='stylesheet', href='css/search.css'),
            Link(rel='stylesheet', href='https://fonts.googleapis.com/css2?family=BhuTuka+Expanded+One&family=JetBrains+Mono:ital,wght@0,100..800;1,100..800&display=swap'),
            htmx_script,
            Title('HalluciNet'),
            Main(
                toolbar(),
                Div(
                    nav(),
                    home_page(),
                    cls='content-view'
                ),
            )
        )

shutdown_event = signal_shutdown()

class SearchResult:
    def __init__(self, title, url, description):
        self.title = title
        self.description = description
        self.url = url
    def __ft__(self):
        return Div(
            A(H2(self.title), href=self.url),
            A(P(self.url), href=self.url),
            P(self.description),
            cls='search-result'
        )

def search_results(query,h_results):
    search_results_top_bar = search_bar(query)
    search_results = Div(
        *[SearchResult(*result) for result in h_results],
        cls='search-results-container'
    )
    return Div(search_results_top_bar, search_results, cls='search-results')


@app.route('/search-progress')
def search_progress(session):
    if 'session_id' not in session: session['session_id'] = str(uuid.uuid4())
    session_id = session['session_id']
    if session_id not in searchers:

        searcher = SearchEngine('local', base_url='https://api.together.xyz/v1', 
                        api_key=LOCAL_LLM_KEY,
                        model_name='meta-llama/Llama-3.3-70B-Instruct-Turbo')
        searchers[session_id] = searcher
    else:
        searcher = searchers[session_id]
    def generate():
        while not shutdown_event.is_set():
            try:
                progress_data = searcher.progress_queue.get()
                progress_html = (
                    Div(
                        Div(cls='progress-fill', style=f'width: {progress_data["progress"]}%;'),cls='progress-bar',
                    ),
                    Div(progress_data['message'], cls='progress-message'),
                    
                )
                if progress_data["status"] == "completed":
                    yield sse_message(progress_html,'progress')
                    yield sse_message(progress_html,'completed')
                    break
                else:
                    yield sse_message(progress_html,'progress')
                print(progress_html)
                
                if progress_data["status"] in ["completed", "error"]:
                    break
            except queue.Empty:
                continue
    return EventStream(generate())

@app.route('/search')
def search(query:str, request:Request, session):
    # now we init the searcher here to avoid mixing up the progress when there are multiple requests
    #searcher = SearchEngine('gemini', api_key=GEMINI_KEY, model_name="gemini-1.5-flash")
    if 'session_id' not in session: session['session_id'] = str(uuid.uuid4())
    session_id = session['session_id']
    if session_id not in searchers:
        searcher = SearchEngine('local', base_url='https://api.together.xyz/v1', 
                        api_key=LOCAL_LLM_KEY,
                        model_name='meta-llama/Llama-3.3-70B-Instruct-Turbo')
        searchers[session_id] = searcher
    else:
        searcher = searchers[session_id]

    query = query.strip()
    results_j = get_or_set(domain='query',key=query,callback=searcher.search,query=query,max_results=10)
    searcher.progress_queue.put({"status": "completed", "message": "Enjoy, I guess.", "progress": 100})
    results = results_j['results']
    results = [(result['title'],result['url'],result['description']) for result in results]

    url_path = request.url.path
    encoded_params = request.url.query
    display_url = f"hallucinet.hln{url_path}?{encoded_params}"


    htmx_script = Script("""document.body.addEventListener('htmx:beforeRequest', function(event) {
    if (event.detail.elt.matches('input[name="query"]')) {
        document.getElementById('search-progress').classList.remove('hidden');
    }
});

document.body.addEventListener('htmx:afterRequest', function(event) {
    if (event.detail.elt.matches('input[name="query"]')) {
        setTimeout(() => {
            document.getElementById('search-progress').classList.add('hidden');
        }, 1000);
    }
});""")
    # if its a reload, we return with all the hearders
    if request.headers.get('HX-Request') == 'true':
        return (
        Link(rel='stylesheet', href='css/search.css'),
        toolbar(display_url),
        Title(f'{query} - Hallucinet'),
        search_results(query,results)
    )
    else:
        return (
        Link(rel='stylesheet', href='css/homepage.css'),
        Link(rel='stylesheet', href='css/search.css'),
        Link(rel='stylesheet', href='https://fonts.googleapis.com/css2?family=BhuTuka+Expanded+One&family=JetBrains+Mono:ital,wght@0,100..800;1,100..800&display=swap'),
        htmx_script,
        Title('HalluciNet'),
        Main(
            toolbar(display_url),
            Div(
                search_results(query,results),
                cls='content-view'
            ),
        )
    )

@app.route('/refresh')
def refresh(request:Request, url:str):
    # if the url is of a search page, we clear the cache for that query
    # works as expected, but commenting out for now
    # if 'search' in url:
    #     query = url.split('=')[-1]
    #     r.delete(f"query:{query}")
    
    return Redirect(url)

@app.route('/resolvehrl')
def resolve_hrl(url:str):
    if url == 'hallucinet.hln':
        return Redirect('/')
    elif 'search' in url:
        query = url.split('=')[-1]
        return Redirect(f'/search?query={query}')
    elif r.exists(f"page:{url}"):
        return json.loads(r.get(f"page:{url}"))
    else:
        return RedirectResponse('/404')


serve()