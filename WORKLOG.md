## 1. Introduction

File esterno , serve a noi sviluppatori per tenere traccia di cio che è stato fatto e cio che è da fare


## Architecture decisions

- Chosen backend framework: FastAPI
- Chosen frontend framework: React with Vite
- Chosen database: PostgreSQL
- Broker forwards incoming measurements to replicated processing services via HTTP
- Processing services are replicated three times
- Each processing replica maintains an in-memory sliding window per sensor
- Sliding window size: 5 seconds
- Sampling rate: 20 Hz
- Samples per window: 100
- Event classification is based on dominant frequency extracted through FFT
- Duplicate-safe persistence is implemented with a deterministic event identifier and a database uniqueness constraint
- Gateway acts as the single entry point for the frontend


## Database setup

- PostgreSQL selected as shared persistence layer
- Database name: seismicdb
- User: seismic_user
- Table initialized automatically through docker-entrypoint-initdb.d
- Initial table: detected_eventscd

## Processing service implementation

- Implemented FastAPI processing service
- Added /health endpoint
- Added /measurements endpoint
- Added per-sensor sliding window manager
- Added FFT-based dominant frequency extraction
- Added frequency-based event classification
- Added PostgreSQL persistence with ON CONFLICT DO NOTHING
- Created three processing replicas in Docker Compose


## Fault tolerance integration

- Added simulator service to Docker Compose
- Added SSE control stream listener to each processing replica
- Each processing replica connects to /api/control
- On SHUTDOWN command, the replica terminates itself
- This behavior implements the failure simulation required by the specification



## Struttura cartelle

### Root repository

- `README.md`  
  Descrizione generale del progetto, overview del sistema e istruzioni principali di utilizzo.

- `input.md`  
  Documento richiesto dalla specifica. Contiene system description, user stories, standard event schema e rule model.

- `Student_doc.md`  
  Documento tecnico richiesto dalla specifica. Descrive container, microservizi, porte, endpoint, persistenza e struttura del sistema.

- `WORKLOG.md`  
  Documento interno di tracciamento del lavoro svolto, delle decisioni architetturali e dello stato corrente del progetto.

- `booklets/`  
  Cartella destinata a contenere materiali di supporto alla consegna, come slide, mockup, raccolta user stories e altri allegati utili.

### Source folder

- `source/`  
  Contiene tutto il codice sorgente del sistema, i file di infrastruttura, Docker Compose, Dockerfiles e configurazioni dei servizi.

#### Infrastructure

- `source/docker-compose.yml`  
  File principale di orchestrazione Docker Compose. Definisce servizi, repliche, networking, environment variables e volumi del sistema.

#### Database

- `source/db/`  
  Cartella dedicata ai file del database.

- `source/db/init/`  
  Cartella contenente gli script SQL eseguiti in fase di inizializzazione del database.

- `source/db/init/001_init.sql`  
  Script SQL iniziale che crea la tabella `detected_events` usata per la persistenza degli eventi rilevati.

#### Broker service

- `source/broker-service/`  
  Cartella del servizio broker. Conterrà il codice del componente che legge i dati dal simulatore e li redistribuisce alle repliche di processing.

- `source/broker-service/Dockerfile`  
  Dockerfile del broker service.

- `source/broker-service/requirements.txt`  
  Dipendenze Python del broker service.

- `source/broker-service/app/`  
  Cartella prevista per il codice applicativo del broker service.

#### Processing service

- `source/processing-service/`  
  Cartella del servizio di processing. Contiene il codice che riceve misure, gestisce sliding window, esegue FFT, classifica eventi e li salva nel database.

- `source/processing-service/Dockerfile`  
  Dockerfile del processing service.

- `source/processing-service/requirements.txt`  
  Dipendenze Python del processing service.

- `source/processing-service/app/`  
  Cartella principale del codice Python del processing service.

- `source/processing-service/app/config.py`  
  Gestisce la configurazione del servizio tramite variabili d’ambiente, inclusi parametri DB, replica ID, sampling rate e dimensione finestra.

- `source/processing-service/app/schemas.py`  
  Definisce gli schemi dati usati dalle API, in particolare il payload delle misure in ingresso e la risposta di health check.

- `source/processing-service/app/sliding_window.py`  
  Implementa la gestione delle sliding windows per sensore, mantenendo in memoria gli ultimi campioni ricevuti.

- `source/processing-service/app/fft_analysis.py`  
  Contiene la logica di analisi in frequenza tramite FFT e il calcolo della peak amplitude.

- `source/processing-service/app/classifier.py`  
  Applica le regole di classificazione degli eventi in base alla frequenza dominante.

- `source/processing-service/app/persistence.py`  
  Gestisce la connessione a PostgreSQL, la generazione dell’identificatore univoco dell’evento e il salvataggio duplicate-safe nel database.

- `source/processing-service/app/deduplication.py`  
  Implementa una deduplicazione in memoria per evitare il salvataggio ripetuto di eventi quasi identici generati da finestre sovrapposte.

- `source/processing-service/app/main.py`  
  Entry point FastAPI del processing service. Espone gli endpoint `/health` e `/measurements` e coordina ricezione dati, analisi, classificazione e persistenza.

#### Gateway service

- `source/gateway-service/`  
  Cartella del gateway service. Conterrà il punto unico di accesso tra frontend e backend.

- `source/gateway-service/Dockerfile`  
  Dockerfile del gateway service.

- `source/gateway-service/requirements.txt`  
  Dipendenze Python del gateway service.

- `source/gateway-service/app/`  
  Cartella prevista per il codice applicativo del gateway service.

#### Frontend dashboard

- `source/frontend-dashboard/`  
  Cartella prevista per il frontend della dashboard real-time.

#### Simulator support

- `source/simulator/`  
  Cartella di supporto per eventuali note o file relativi all’integrazione del simulatore, senza modificare il container fornito.

#### Technical documentation

- `source/docs/`  
  Cartella destinata a contenere documentazione tecnica interna al progetto.

- `source/docs/architecture/`  
  Cartella destinata ai diagrammi architetturali del sistema.

- `source/docs/mockups/`  
  Cartella destinata ai mockup low-fidelity richiesti dalla specifica.