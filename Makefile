TEST_DATABASE := database-test.db
DEV_DATABASE  := database-dev.db

test-win:
	del /q $(TEST_DATABASE)
	pytest tests
	rmdir /s /q "tests\__pycache__"
	rmdir /s /q ".pytest_cache"

test:
	pytest tests
	rm $(TEST_DATABASE)
	rm -rf "tests\__pycache__"
	rm -rf ".pytest_cache"

coverage:
	coverage run --source=carpi -m pytest tests
	coverage xml

run:
	uvicorn carpi.main:app

run-reload:
	uvicorn carpi.main:app --reload

clean-win:
	del /q "$(DEV_DATABASE)"
	rmdir /s /q "carpi\__pycache__"

clean:
	rm $(DEV_DATABASE)
	rm -rf carpi\__pycache__

clear:
	del /q $(DEV_DATABASE)
	del /q $(TEST_DATABASE)

docker-build:
	docker build -t carpi .

docker-run:
	docker run -p 5000:80 carpi