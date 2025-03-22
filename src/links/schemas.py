from pydantic import BaseModel, HttpUrl, field_serializer

    
class NewLink(BaseModel):
    link: HttpUrl
    
    @field_serializer('link')
    def serealize_link(self, link: HttpUrl):
        return str(link)
