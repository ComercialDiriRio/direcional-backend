# !pip install fastapi uvicorn pandas gspread oauth2client python-multipart
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import uvicorn

app = FastAPI()

# Permite que o Next.js (Frontend) converse com o Python (Backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELOS ---
class SimulacaoRequest(BaseModel):
    renda: float
    valor_venda: float
    prazo: int = 360
    sistema: str = "SAC"

# --- LÓGICA DE CÁLCULO PROFISSIONAL ---
@app.post("/api/calcular")
async def calcular(data: SimulacaoRequest):
    i_anual = 8.16 / 100
    i_mensal = (1 + i_anual)**(1/12) - 1
    
    # PRICE
    pmt_price = data.valor_venda * (i_mensal * (1 + i_mensal)**data.prazo) / ((1 + i_mensal)**data.prazo - 1)
    
    # SAC (Primeira Parcela)
    amort = data.valor_venda / data.prazo
    pmt_sac = amort + (data.valor_venda * i_mensal)
    
    return {
        "parcela_price": round(pmt_price, 2),
        "parcela_sac_inicial": round(pmt_sac, 2),
        "financiamento_maximo": round(data.renda * 45, 2) # Exemplo de regra de negócio
    }

# Rota para o Render verificar se o app está vivo
@app.get("/")
def home():
    return {"status": "Sistema Direcional Online"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)