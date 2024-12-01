from pydantic import BaseModel, Field
from agency_swarm.tools import BaseTool
import os

class DeleteTool(BaseTool, BaseModel):

    file_path: str = Field(
        ..., description="File path to the file being deleted."
    )

    def run(self):
        try:
            if os.path.isfile(self.file_path):
                os.remove(self.file_path)
                return True
            else:
                print(f"File not found: {self.file_path}")
                return False
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
        
delete_tool = DeleteTool