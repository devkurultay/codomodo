#!/bin/bash
# npm run build
source env/bin/activate
python manage.py collectstatic --noinput
# Bundle up an archive file
tar -cf kodjaz.tar authentication/ config/ courses/ fixtures/ frontend/ staticfiles/ requirements/ users/ manage.py robots.txt .env
# Load variables form .env file
source .env
# Upload bundled archive
scp kodjaz.tar $SERVER_USERNAME@$SERVER_IP:$PROJECT_FOLDER_ON_SERVER/
rm kodjaz.tar
ssh -tt $SERVER_USERNAME@$SERVER_IP << END
    cd $PROJECT_FOLDER_ON_SERVER/
    tar -xf kodjaz.tar

    sed -i 's/DEBUG=True/DEBUG=False/' .env

    source env/bin/activate && echo 'Activated env' || sudo apt install python3.8-venv --yes && python3 -m venv env && source env/bin/activate && echo 'Installed venv and activated env';
    echo "Now installing python packages"
    pip install --upgrade pip
    pip install -r requirements/requirements_prod.txt
    echo "Applying migrations"
    python manage.py migrate --noinput --settings=config.settings_prod
    echo "Exiting"
    exit
END
