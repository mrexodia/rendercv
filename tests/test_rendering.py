import unittest
import os
from datetime import date
import shutil

from rendercv import rendering, data_model

from pydantic import ValidationError


class TestDataModel(unittest.TestCase):
    def test_markdown_to_latex(self):
        input = "[link](www.example.com)"
        expected = r"\hrefExternal{www.example.com}{link}"
        output = rendering.markdown_to_latex(input)
        with self.subTest(msg="only one link"):
            self.assertEqual(output, expected)

        input = "[link](www.example.com) and [link2](www.example2.com)"
        expected = (
            r"\hrefExternal{www.example.com}{link} and"
            r" \hrefExternal{www.example2.com}{link2}"
        )
        output = rendering.markdown_to_latex(input)
        with self.subTest(msg="two links"):
            self.assertEqual(output, expected)

        input = "[**link**](www.example.com)"
        expected = r"\hrefExternal{www.example.com}{\textbf{link}}"
        output = rendering.markdown_to_latex(input)
        with self.subTest(msg="bold link"):
            self.assertEqual(output, expected)

        input = "[*link*](www.example.com)"
        expected = r"\hrefExternal{www.example.com}{\textit{link}}"
        output = rendering.markdown_to_latex(input)
        with self.subTest(msg="italic link"):
            self.assertEqual(output, expected)

        input = "[*link*](www.example.com) and [**link2**](www.example2.com)"
        expected = (
            r"\hrefExternal{www.example.com}{\textit{link}} and"
            r" \hrefExternal{www.example2.com}{\textbf{link2}}"
        )
        output = rendering.markdown_to_latex(input)
        with self.subTest(msg="italic and bold links"):
            self.assertEqual(output, expected)

        input = "**bold**, *italic*, and [link](www.example.com)"
        expected = (
            r"\textbf{bold}, \textit{italic}, and"
            r" \hrefExternal{www.example.com}{link}"
        )
        output = rendering.markdown_to_latex(input)
        with self.subTest(msg="bold, italic, and link"):
            self.assertEqual(output, expected)

        # invalid input:
        input = 20
        with self.subTest(msg="float input"):
            with self.assertRaises(ValueError):
                rendering.markdown_to_latex(input)

    def test_markdown_link_to_url(self):
        input = "[link](www.example.com)"
        expected = "www.example.com"
        output = rendering.markdown_link_to_url(input)
        with self.subTest(msg="only one link"):
            self.assertEqual(output, expected)

        input = "[**link**](www.example.com)"
        expected = "www.example.com"
        output = rendering.markdown_link_to_url(input)
        with self.subTest(msg="bold link"):
            self.assertEqual(output, expected)

        input = "[*link*](www.example.com)"
        expected = "www.example.com"
        output = rendering.markdown_link_to_url(input)
        with self.subTest(msg="italic link"):
            self.assertEqual(output, expected)

        # invalid input:
        input = 20
        with self.subTest(msg="float input"):
            with self.assertRaises(ValueError):
                rendering.markdown_link_to_url(input)

        input = "not a markdown link"
        with self.subTest(msg="invalid input"):
            with self.assertRaises(ValueError):
                rendering.markdown_link_to_url(input)

        input = "[]()"
        with self.subTest(msg="empty link"):
            with self.assertRaises(ValueError):
                rendering.markdown_link_to_url(input)

    def test_make_it_bold(self):
        input = "some text"
        expected = r"\textbf{some text}"
        output = rendering.make_it_bold(input)
        with self.subTest(msg="without match_str input"):
            self.assertEqual(output, expected)

        input = "some text"
        match_str = "text"
        expected = r"some \textbf{text}"
        output = rendering.make_it_bold(input, match_str)
        with self.subTest(msg="with match_str input"):
            self.assertEqual(output, expected)

        input = 20
        with self.subTest(msg="float input"):
            with self.assertRaises(ValueError):
                rendering.make_it_bold(input)

    def test_make_it_underlined(self):
        input = "some text"
        expected = r"\underline{some text}"
        output = rendering.make_it_underlined(input)
        with self.subTest(msg="without match_str input"):
            self.assertEqual(output, expected)

        input = "some text"
        match_str = "text"
        expected = r"some \underline{text}"
        output = rendering.make_it_underlined(input, match_str)
        with self.subTest(msg="with match_str input"):
            self.assertEqual(output, expected)

        input = 20
        with self.subTest(msg="float input"):
            with self.assertRaises(ValueError):
                rendering.make_it_underlined(input)

    def test_make_it_italic(self):
        input = "some text"
        expected = r"\textit{some text}"
        output = rendering.make_it_italic(input)
        with self.subTest(msg="without match_str input"):
            self.assertEqual(output, expected)

        input = "some text"
        match_str = "text"
        expected = r"some \textit{text}"
        output = rendering.make_it_italic(input, match_str)
        with self.subTest(msg="with match_str input"):
            self.assertEqual(output, expected)

        input = 20
        with self.subTest(msg="float input"):
            with self.assertRaises(ValueError):
                rendering.make_it_italic(input)

    def test_divide_length_by(self):
        lengths = [
            "10cm",
            "10.24in",
            "10 pt",
            "10.24 mm",
            "10.24    em",
            "1024    ex",
        ]
        divider = 10
        expected = [
            "1.0 cm",
            "1.024 in",
            "1.0 pt",
            "1.024 mm",
            "1.024 em",
            "102.4 ex",
        ]
        for length, exp in zip(lengths, expected):
            with self.subTest(length=length):
                self.assertEqual(rendering.divide_length_by(length, divider), exp)

    def test_get_today(self):
        expected = date.today().strftime("%B %d, %Y")
        result = rendering.get_today()
        self.assertEqual(expected, result)

    def test_get_path_to_font_directory(self):
        font_name = "test"
        expected = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "rendercv",
            "templates",
            "fonts",
            font_name,
        )
        result = rendering.get_path_to_font_directory(font_name)
        self.assertEqual(expected, result)

    def test_render_template(self):
        test_input = {
            "cv": {
                "academic_projects": [
                    {
                        "date": "Spring 2022",
                        "highlights": ["Test 1", "Test 2"],
                        "location": "Istanbul, Turkey",
                        "name": "Academic Project 1",
                        "url": "https://example.com",
                    },
                    {
                        "highlights": ["Test 1", "Test 2"],
                        "name": "Academic Project 2",
                        "url": "https://example.com",
                    },
                    {
                        "end_date": "2022-05-01",
                        "highlights": ["Test 1", "Test 2"],
                        "location": "Istanbul, Turkey",
                        "name": "Academic Project 3",
                        "start_date": "2022-02-01",
                        "url": "https://example.com",
                    },
                ],
                "certificates": [{"name": "Certificate 1"}],
                "education": [
                    {
                        "area": "Mechanical Engineering",
                        "end_date": "1985-01-01",
                        "gpa": "3.80/4.00",
                        "highlights": ["Test 1", "Test 2"],
                        "institution": "Bogazici University",
                        "location": "Istanbul, Turkey",
                        "start_date": "1980-09-01",
                        "study_type": "BS",
                        "transcript_url": "https://example.com/",
                        "url": "https://boun.edu.tr",
                    },
                    {
                        "area": "Mechanical Engineering, Student Exchange Program",
                        "end_date": "2022-01-15",
                        "institution": "The University of Texas at Austin",
                        "location": "Austin, TX, USA",
                        "start_date": "2021-08-01",
                        "url": "https://utexas.edu",
                    },
                ],
                "email": "john@doe.com",
                "extracurricular_activities": [
                    {
                        "company": "Test Company 1",
                        "highlights": [
                            "Lead and train members for intercollegiate alpine ski"
                            " races in Turkey and organize skiing events."
                        ],
                        "position": "Test Position 1",
                    },
                    {
                        "company": "Test Company 1",
                        "date": "Summer 2019 and 2020",
                        "highlights": ["Test 1", "Test 2", "Test 3"],
                        "location": "Izmir, Turkey",
                        "position": "Test Position 1",
                    },
                ],
                "label": "Engineer at CERN",
                "location": "Geneva, Switzerland",
                "name": "John Doe",
                "personal_projects": [{"name": "Personal Project 1"}],
                "phone": "+905413769286",
                "publications": [
                    {
                        "authors": [
                            "Cetin Yilmaz",
                            "Gregory M Hulbert",
                            "Noboru Kikuchi",
                        ],
                        "cited_by": 243,
                        "date": "2007-08-01",
                        "doi": "10.1103/PhysRevB.76.054309",
                        "journal": "Physical Review B",
                        "title": (
                            "Phononic band gaps induced by inertial amplification in"
                            " periodic media"
                        ),
                    }
                ],
                "section_order": [
                    "Education",
                    "Work Experience",
                    "Academic Projects",
                    "Certificates",
                    "Personal Projects",
                    "Skills",
                    "Test Scores",
                    "Extracurricular Activities",
                    "Publications",
                ],
                "skills": [
                    {
                        "details": "C++, C, Python, JavaScript, MATLAB, Lua, LaTeX",
                        "name": "Programming",
                    },
                    {"details": "GMSH, GetDP, CalculiX", "name": "CAE"},
                ],
                "social_networks": [
                    {"network": "LinkedIn", "username": "dummy"},
                    {"network": "GitHub", "username": "sinaatalay"},
                ],
                "test_scores": [
                    {"date": "2022-10-01", "details": "120/120", "name": "TOEFL"},
                    {
                        "details": "9.0/9.0",
                        "name": "IELTS",
                        "url": "https://example.com",
                    },
                ],
                "website": "https://example.com",
                "work_experience": [
                    {
                        "company": "Company 1",
                        "end_date": "present",
                        "highlights": ["Test 1", "Test 2", "Test 3"],
                        "location": "Geneva, Switzerland",
                        "position": "Position 1",
                        "start_date": "2023-02-01",
                        "url": "https://example.com",
                    },
                    {
                        "company": "Company 2",
                        "end_date": "2023-02-01",
                        "highlights": ["Test 1", "Test 2", "Test 3"],
                        "location": "Geneva, Switzerland",
                        "position": "Position 2",
                        "start_date": "1986-02-01",
                        "url": "https://example.com",
                    },
                ],
            },
            "design": {
                "font": "EBGaramond",
                "options": {
                    "date_and_location_width": "3.6 cm",
                    "margins": {
                        "entry_area": {
                            "left": "0.2 cm",
                            "right": "0.2 cm",
                            "vertical_between": "0.12 cm",
                        },
                        "highlights_area": {
                            "left": "0.6 cm",
                            "top": "0.12 cm",
                            "vertical_between_bullet_points": "0.07 cm",
                        },
                        "page": {
                            "bottom": "1.35 cm",
                            "left": "1.35 cm",
                            "right": "1.35 cm",
                            "top": "1.35 cm",
                        },
                        "section_title": {"bottom": "0.13 cm", "top": "0.13 cm"},
                    },
                    "primary_color": "rgb(0,79,144)",
                    "show_last_updated_date": True,
                    "show_timespan_in_experience_entries": True,
                },
                "theme": "classic",
            },
        }
        data = data_model.RenderCVDataModel(**test_input)
        rendering.render_template(data=data, output_path=os.path.dirname(__file__))

        # Check if the output file exists:
        output_folder_path = os.path.join(os.path.dirname(__file__), "output")
        output_file_path = os.path.join(output_folder_path, "John_Doe_CV.tex")
        self.assertTrue(os.path.exists(output_file_path))

        # Compare the output file with the reference file:
        reference_file_path = os.path.join(
            os.path.dirname(__file__), "reference_files", "John_Doe_CV.tex"
        )
        with open(output_file_path, "r") as file:
            output = file.read()
        with open(reference_file_path, "r") as file:
            reference = file.read()

        self.assertEqual(output, reference)

        # Check if the font directory exists:
        font_directory_path = os.path.join(output_folder_path, "fonts")
        self.assertTrue(os.path.exists(font_directory_path))

        required_files = [
            "EBGaramond-Italic.ttf",
            "EBGaramond-Regular.ttf",
            "EBGaramond-Bold.ttf",
            "EBGaramond-BoldItalic.ttf",
        ]
        font_files = os.listdir(font_directory_path)
        for required_file in required_files:
            with self.subTest(required_file=required_file):
                self.assertIn(required_file, font_files)

        # Remove the output directory:
        shutil.rmtree(output_folder_path)


if __name__ == "__main__":
    unittest.main()
