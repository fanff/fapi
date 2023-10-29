# assuming here I am on a pytorch docker image
mkdir -p /workspace; env | grep _ >> /etc/environment; touch ~/.no_auto_tmux; sleep 1;

# conda init bash
. /opt/conda/etc/profile.d/conda.sh

conda activate base
conda create -n fapi python=3.10 -y
conda activate fapi

pip install git+https://github.com/fanff/fapi.git
cd fapi

pip install python-dotenv
pip install fastapi 
pip install openai-whisper
pip install uvicorn

uvicorn fapi:app
