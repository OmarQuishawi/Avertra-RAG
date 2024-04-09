 FROM python:3.10 

 WORKDIR /utility_rag
 
 COPY requirements.txt .
 
 COPY ./data ./data

 COPY ./storage ./storage

 RUN pip install -r requirements.txt

 ADD utility_RAG.py .
                                                                     
 CMD [ "python" , "./utility_RAG.py"]                                                                                                                         