# Guide to run

## Prerequisite

- Docker installed and running
- OS with bash scripting enabled (Ubuntu, Linux AMI, MacOS). Windows systems need to have [**gitbash**](https://git-scm.com/download/win)
- User context used must have access to docker services. In most cases, use sudo su to switch as root user
- Use the terminal (or gitbash) window to run all the future steps.
- Python 3.9+
- pip installed
- Download data files from [**Drive**](https://drive.google.com/file/d/11O0lo6GNMwb1X9mv0OztBvNrVVJhBQjv/view?usp=drive_link)

## Data processing (optional)

```bash
unzip source_code.zip
cd source_code
```

Install requirements

```bash
cd backend/data_processing
mv ~/data ./
pip install -r requirements.txt
```

Run data processing

### Resume data processing

```bash
python process_resume_data.py
```

### Resume data processing

```bash
python process_job_data.py
```

## Application

```bash
cd source_code
docker-compose up -d
```

Visit https://project-dam501.mse20hcm.top

Thank you!
