TEST_DATABASE := database-test.db
DEV_DATABASE  := database-dev.db

test-win:
	pytest tests
	del $(TEST_DATABASE)
	rmdir /s /q "tests\__pycache__"
	rmdir /s /q ".pytest_cache"

test:
	pytest tests
	rm $(TEST_DATABASE)
	rm -rf "tests\__pycache__"
	rm -rf ".pytest_cache"

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