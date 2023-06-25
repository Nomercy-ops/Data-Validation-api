from pydantic import BaseModel
from pydantic import BaseModel



class ValidationResult(BaseModel):
    name: str
    count: int
    mismatch: str

class FormData(BaseModel):
    columns_to_remove: str

# class ValidationRequest(BaseModel):
#     source: str
#     target: str
#     source_csv: UploadFile = File(...)
#     target_csv: UploadFile = File(...)
