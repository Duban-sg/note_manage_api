from src.model import NoteIn,Note,CategoriaIn,Categoria
from typing import List
from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
from datetime import date
import src.persistence.mongo_db.main as mongo_db
from pydantic import json
from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import get_var
from bson import ObjectId
from src.core.utils import getParamsToUpdate
from src.notification.notificarDecorator import notificar


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


json.ENCODERS_BY_TYPE[ObjectId]=str
basededatos = mongo_db.mongo_db()
basededatos.setNameDatabase('note_manage')
basededatos.setNameCollection('categories')

@app.get("/health/")
async def saveNotes():
    return get_var("my_ip")


@app.post("/notas/{categoryId}")
@notificar(nombreModulo="/notas/{categoryId}")
async def saveNotes( categoryId:str,noteIn:NoteIn.NoteIn):
    try:
        responseCDb = basededatos.getOneDocumentInCollection(categoryId)
        if responseCDb:
            note = Note.Note(**noteIn.dict(), fecha_creacion = str(date.today()))
            resutl = basededatos.insertObjectInDocumentByidInColeccion(categoryId,note.dict())
            if resutl:
                responseCDb = basededatos.getOneDocumentInCollection(categoryId)
                return responseCDb
            else: 
                raise HTTPException(status_code=400, detail="No se pudo actualizar la categoria")
        else: 
            raise HTTPException(status_code=404, detail="Note Not found")
    except :
        raise HTTPException(status_code=500, detail="Internal Error Server")


@app.put("/notas/{idcategoria}/{idnote}")
@notificar(nombreModulo="/notas/{idcategoria}/{idnote}")
def updateNotes(idcategoria:str,idnote: str,noteIn:NoteIn.NoteIn) :
    noteIn = jsonable_encoder(noteIn)
    resutl = basededatos.updateDocumentByFilterInCollecction(
        {"_id":ObjectId(idcategoria),"notes._id":ObjectId(idnote)},
        {**getParamsToUpdate("notes.$.",noteIn), "notes.$.fecha_modificacion":str(date.today()) })
    if resutl :
        Note = basededatos.getOneDocumentInCollection(idcategoria)
        return Note
    else :
        raise HTTPException(status_code=404, detail="Note Not found")

@app.delete("/notas/{idcategoria}/{idnote}")
@notificar(nombreModulo="/notas/{idcategoria}/{idnote}")
def delete_note(idcategoria: str,idnote: str): 
    result = basededatos.removeObjectInDocumentByidInColeccion(idcategoria,idnote)
    if result :
        responseCDb = basededatos.getOneDocumentInCollection(idcategoria)
        return responseCDb
    else :
        raise HTTPException(status_code=404, detail = "Note not found")
    
@app.get("/categorias/")
@notificar(nombreModulo="/categorias/")
def getCategorias() :
    resutl = basededatos.getAllDocumentInCollection()
    return resutl

@app.get("/categorias/{idAutor}")
@notificar(nombreModulo="/categorias/{idAutor}")
def getCategoriasByAutor(idAutor:str) :

    resutl = basededatos.getAllDocumentInCollection({"autor": idAutor})
    return resutl

    
@app.patch("/categorias/{idcategoria}")
@notificar(nombreModulo="/categorias/{idcategoria}")
def updateNotes(idcategoria: str, newName: str ) :
    resutl = basededatos.updateDocumentByFilterInCollecction(
        {"_id":ObjectId(idcategoria)},
        {"name":newName})
    if resutl :
        Note = basededatos.getOneDocumentInCollection(idcategoria)
        return Note
    else :
        raise HTTPException(status_code=404, detail="Note Not found")

    
@app.delete("/categorias/{idcategoria}")
def deleteCategoria(idcategoria: str): 
    result = basededatos.deleteDocumentByIdInCollecction(idcategoria)
    if result :
        id = idcategoria
        return id
    else :
        raise HTTPException(status_code=404, detail = "Note not found")
    
@app.post("/categorias/")
async def saveNotes( CategoriasIn:CategoriaIn.CategoriaIn):
    note = Categoria.Categoria(**CategoriasIn.dict(), fecha_creacion = str(date.today()))
    resutl = basededatos.insertInColeccition(note.dict())
    response = {**note.dict(), '_id':str(resutl.inserted_id)}
    return response