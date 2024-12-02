from fasthtml.common import *

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
            Input(type='text', placeholder='Search HalluciNet or type a HRL', cls='address-bar'),
            cls='navigation-buttons address-bar-container'
        ),            
        Div(
            Button(I(cls='nf nf-md-bookmark_outline'), title='Bookamark', cls='navigation-button'),
            cls='navigation-buttons'
        ),
        cls='toolbar'
    )
    return toolbar

def home_page():
    home_page = Div(
        Div(
            H1('HalluciNet', cls='title'),
            P('The Illusion of Reality', cls='subtitle'),
            cls='header'
        ),
        Div(
            Input(type='text', placeholder='Search HalluciNet...', cls='search-bar'),
            cls='search-bar-container'
        ),
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

serve()