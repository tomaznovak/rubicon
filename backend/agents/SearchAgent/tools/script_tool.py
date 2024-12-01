from agency_swarm.tools import BaseTool
import pdfplumber
from openai import OpenAI
from markd import Markdown
from pydantic import BaseModel, Field
from backend.db import models, database
import os

class Script_Tool(BaseTool, BaseModel):

    file_path: str = Field(
        ..., description="File path to the file that is going to be analyzed."
    )
    id: str = Field(
        ..., description="Unique string which represents the file."
    )
    title: str = Field(
        ..., description="Title of the research paper"
    )
    id: str = Field(
        ..., description="ARXIV id of the given file."
    )


    def run(self):

        db = next(database.get_db())

        with pdfplumber.open(self.file_path) as pdf:
            text = ""        
            for page in pdf.pages:
                text += page.extract_text()

        text.split(maxsplit=10)

        client = OpenAI()

        completion = client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system",
                "content": """
                You are an expert in extracting valuable information from the text chunks and making them into a well rounded text.
                Always list the authors and the title of the research paper first before you procced.
                Format the output text into markdown file.
                """},
                {
                    "role": "user",
                    "content": f"extract the meaningfull and important facts from this text: {text}"
                }
            ]
        )
        response = completion.choices[0].message.content


        markd = Markdown()
        markd.add_text(response)
        markd.save(f"./backend/scripts/script-{self.id}.md")
        file_path = r"C:\Users\Lenovo\Desktop\Mark-2\backend\scripts\script-{}.md".format(self.id)
        with open(file_path, 'rb') as f:
            fdata = f.read()
            new_file = models.MD(name=file_path.split("\s")[-1], title = self.title, data=fdata)
            db.add(new_file)
            db.commit()

        pdf_file_path = r"C:\Users\Lenovo\Desktop\Mark-2\backend\pdfs\paper-{}.pdf".format(self.id)

        ### REMOVE WHEN YOU ARE DEPLOYING ON CLOUD
        try:
            os.remove(file_path)
            os.remove(pdf_file_path)
            print(f"Succesfully removed {file_path} and {pdf_file_path}")
        except Exception as e:
            return f"Error: {str(e)}"        

        return {
                "response": f"Script for the paper {self.id} was succesfully generarated."
            }
    

script_tool = Script_Tool
