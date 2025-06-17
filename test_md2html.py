import unittest
from Main import markdown_to_html

class TestMd2Html(unittest.TestCase):
    def test_basic_features(self):
        md = """---\ntitle: sample\n---\n# Header *one*\n\nParagraph with **bold** and _em_.\n\n![[img.png]]\n\n```sh\necho hello\n```\n"""
        html = markdown_to_html(md, title="sample")
        self.assertIn('<h1>Header <em>one</em></h1>', html)
        self.assertIn('<p>Paragraph with <strong>bold</strong> and <em>em</em>.</p>', html)
        self.assertIn('<img src="../graphics/img.png" alt="img.png">', html)
        self.assertIn('<button class="copy"', html)
        self.assertNotIn('title: sample', html)

    def test_callout(self):
        md = "> [!NOTE] Title\n> body line"
        html = markdown_to_html(md, title="callout")
        self.assertIn('callout-note', html)
        self.assertIn('Title', html)
        self.assertIn('body line', html)

    def test_multiline_latex(self):
        md = """$$\n\\begin{array}{rcl}\n2&5&7 \\\n2&5&7 \\\n\\end{array}\n$$"""
        html = markdown_to_html(md, title="latex")
        self.assertIn("<p>$$", html)
        self.assertIn("\\begin{array}{rcl}", html)
        self.assertIn("2&5&7", html)
        self.assertIn("$$</p>", html)

    def test_pipeline_example(self):
        path = 'Pipeline_example.md'
        md_text = open(path, encoding='utf8').read()
        html = markdown_to_html(md_text, title='pipeline')
        # basic sanity checks
        self.assertIn('<img src="../graphics/pipeline_example.png"', html)
        self.assertIn('<button class="copy"', html)

if __name__ == '__main__':
    unittest.main()
