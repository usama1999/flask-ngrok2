import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="flask-ngrok2",
    version="0.1.0",
    author="Mohamed Rashad",
    description="A successor to flask-ngrok for demo Flask apps using ngrok.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MohamedAliRashad/flask-ngrok2",
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    keywords='flask ngrok2 demo',
    install_requires=['Flask>=0.8', 'requests'],
    py_modules=['flask_ngrok2']
)
