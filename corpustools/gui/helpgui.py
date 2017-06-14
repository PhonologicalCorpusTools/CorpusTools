import os

from .imports import *


class AboutDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self)

        self.help_url = 'http://corpustools.readthedocs.org/en/'
        if hasattr(sys, 'frozen'):
            import corpustools.__version__ as version
            self.help_url += version + '/'
            base_dir = os.path.dirname(sys.executable)
            self.help_dir = os.path.join(base_dir, 'html')
            # if sys.platform == 'win32':
            #     self.help_dir = os.path.join(base_dir, 'html')
            # elif sys.platform == 'darwin':
            #     self.help_dir = os.path.join(base_dir, 'html')
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.help_dir = os.path.join(base_dir, 'docs','build','html')
            #self.help_url += 'develop/'
            self.help_url += 'latest/'
        use_local = os.path.exists(self.help_dir)

        layout = QVBoxLayout()

        self.webView = QWebView(self)

        if use_local:
            about_page = os.path.join(self.help_dir,'about.html')
            url = QUrl.fromLocalFile(about_page)
        else:
            about_page = self.help_url + 'about.html'
            url = QUrl(about_page)
        self.webView.setUrl(url)

        layout.addWidget(self.webView)

        self.setLayout(layout)
        self.setWindowTitle('About PCT')


class HelpDialog(QDialog):
    def __init__(self, parent, name = None, section = None):
        QDialog.__init__(self)
        self.help_url = 'http://corpustools.readthedocs.org/en/'
        if hasattr(sys, 'frozen'):
            from corpustools import __version__ as version
            self.help_url += 'v' + version + '/'
            base_dir = os.path.dirname(sys.executable)
            if sys.platform == 'win32':
                self.help_dir = os.path.join(base_dir, 'html')
            elif sys.platform == 'darwin':
                self.help_dir = os.path.join(base_dir, 'docs','build','html')
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

            self.help_dir = os.path.join(base_dir, 'docs','build','html')
            # self.help_url += 'develop/'
            self.help_url += 'latest/'
        use_local = os.path.exists(self.help_dir)
        layout = QVBoxLayout()

        self.webView = QWebView(self)

        html_name = 'index.html'
        if name:

            html_name = '{}.html'.format(name.lower().replace(' ','_'))
            if name == 'phonological search':
                html_name = 'transcriptions_and_feature_systems.html'
                section = 'phonological-search'
            self.setWindowTitle('About {}'.format(name.lower()))
        else:
            self.setWindowTitle('PCT help')
        help_url = self.help_url + html_name
        if use_local:
            help_local = os.path.join(self.help_dir,html_name)

            url = QUrl.fromLocalFile(help_local)
        else:
            url = QUrl(help_url)
        if section:
            url.setFragment(section)
        self.webView.setUrl(url)

        self.urlLabel = QLabel("<qt>Online documentation available at \
                        <a href = \"{}\">{}</a>.</qt>".format(help_url, help_url))
        self.urlLabel.setWordWrap(True)
        self.urlLabel.linkActivated.connect(self.openURL)
        layout.addWidget(self.urlLabel)
        layout.addWidget(self.webView)

        self.setLayout(layout)

    def openURL(self, URL):
        QDesktopServices().openUrl(QUrl(URL))