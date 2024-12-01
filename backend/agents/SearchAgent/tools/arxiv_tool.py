import arxiv
from pydantic import Field, BaseModel
from agency_swarm import BaseTool
from backend.db import models, database
from sqlalchemy import exists


class ARXIVTool(BaseTool, BaseModel):

    keyword: str = Field(
        ..., description="Gives information for what is the search keyword."
    )
    
    def run(self):

        client = arxiv.Client()

        db = next(database.get_db())

        search = arxiv.Search(
                query = f"ti:{self.keyword}",
                max_results = 1,
                sort_by = arxiv.SortCriterion.Relevance
                )       

        results = client.results(search)
        all_results = list(results)
        if not all_results:
            return "No results found"
        
        for a in all_results:
            paper_id = a.entry_id.split('/')[-1]
            filename = f"paper-{paper_id}.pdf"
            title = a.title

            if not db.query(exists().where(models.Papers.arxiv_id == paper_id)).scalar():
                paper = next(arxiv.Client().results(arxiv.Search(id_list=[paper_id])))
                paper.download_pdf(dirpath="/Users/Lenovo/Desktop/Mark-2/backend/pdfs/", filename=f"paper-{paper_id}.pdf")
                new_article = models.Papers(arxiv_id=paper_id, title=title)
                db.add(new_article)
                file_path = r"C:\Users\Lenovo\Desktop\Mark-2\backend\pdfs\{}".format(filename)
                with open(file_path, 'rb') as f:
                    fdata = f.read()
                    file = models.PDF(name=file_path.split("\p")[-1], title=title, data=fdata)
                    db.add(file)
                db.commit()
                
                return f"File {filename} was downloaded successfully and uploaded to database. Continue with the next step"
    
        return f"Paper with the title {title} and id {paper_id} was already downloaded."

arxiv_tool = ARXIVTool
