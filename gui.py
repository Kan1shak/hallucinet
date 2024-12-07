# TODO: Make the toolabr buttons functional
# TODO: Make the address bar on the toolbar functional
# TODO: Add a settings page
# TODO: Work on reflections page

import json
import redis
from fasthtml.common import *
from web import SearchEngine

import dotenv

dotenv.load_dotenv('.env')
GEMINI_KEY = os.getenv('GEMINI_KEY')
#searcher = SearchEngine('gemini', api_key=GEMINI_KEY, model_name="gemini-1.5-flash")

# a local version of the searcher
LOCAL_LLM_KEY = os.getenv('LOCAL_LLM_KEY')
searcher = SearchEngine('local', base_url='https://api.together.xyz/v1', 
                        api_key=LOCAL_LLM_KEY,
                        model_name='meta-llama/Llama-3.3-70B-Instruct-Turbo')

r = redis.Redis()

def get_or_set(domain:str, key:str, callback, **kwargs):
    if r.exists(f"{domain}:{key}"):
        return json.loads(r.get(f"{domain}:{key}"))
    else:
        value = callback(**kwargs)
        r.set(f"{domain}:{key}",json.dumps(value))
        return value

app, rt = fast_app(
    pico=False,static_path='static',
    hdrs=(Link(rel='stylesheet', href='https://www.nerdfonts.com/assets/css/webfont.css'),
        Link(rel='stylesheet', href='css/toolbar.css'),
        Link(rel='stylesheet', href='css/global.css'),
        Link(rel='preconnect', href='hhttps://fonts.googleapis.com'),
        Link(rel='preconnect', href='https://fonts.gstatic.com', crossorign=True),
    )
)

def nav():
    nav = Ul(
        Li(A('Behind the Illusion', hx_get='/about')),
        Li(A('Reflections', hx_get='/reflections')),
        Li(A('Tune your Oracle', hx_get='/settings')),
        cls='navbar'
    )
    return Nav(nav)

def toolbar():
    toolbar = Div(
        Div(
            Div(
                Button(I(cls='nf nf-fa-angle_left'), title='Go Back', cls='navigation-button'),
                Button(I(cls='nf nf-fa-angle_right'), title='Go Forward', cls='navigation-button'),
                cls='navigation-buttons',
            ),
            Div(
                Button(I(cls='nf nf-md-refresh'), title='Refresh Page', cls='navigation-button'),
                Button(I(cls='nf nf-fa-home'),title='Home Page', cls='navigation-button'),
                cls='navigation-buttons'
            ),
            cls='navigation-buttons-container'
        ),
        Div(
            Input(type='text', value='hallucinet.start',placeholder='Search HalluciNet or type a HRL', cls='address-bar'),
            cls='navigation-buttons address-bar-container'
        ),            
        Div(
            Button(I(cls='nf nf-md-bookmark_outline'), title='Bookamark', cls='navigation-button'),
            cls='navigation-buttons'
        ),
        cls='toolbar'
    )
    return toolbar

def search_bar(prefill:str=None):
    return  Div(Input(type='text', placeholder='Search HalluciNet...', cls='search-bar', name='query',
            value=prefill,
            hx_get='/search', hx_target='.content-view', hx_trigger="keyup[key=='Enter']"),
            cls='search-bar-container'
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
def index():
    return (
        Link(rel='stylesheet', href='css/homepage.css'),
        Link(rel='stylesheet', href='css/search.css'),
        Link(rel='stylesheet', href='https://fonts.googleapis.com/css2?family=BhuTuka+Expanded+One&family=JetBrains+Mono:ital,wght@0,100..800;1,100..800&display=swap'),
        Main(
            toolbar(),
            Div(
                Title('HalluciNet'),
                nav(),
                home_page(),
                cls='content-view'
            ),
        )
    )


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

@app.route('/search')
def search(query:str):
    query = query.strip()
    results_j = get_or_set(domain='query',key=query,callback=searcher.search,query=query,max_results=10)
    results = results_j['results']
    results = [(result['title'],result['url'],result['description']) for result in results]

    return (
        Title(f'{query} - Hallucinet'),
        search_results(query,results)
    )

serve()