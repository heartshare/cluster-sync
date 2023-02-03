from setuptools import setup, find_packages

setup(
    name="cluster-sync",
    description="A lightweight Docker Swarm compatible script to synch a directory between N nodes",
    version="0.0.1",
    author="Hedley Roos",
    author_email="hedleyroos@gmail.com",
    license="BSD",
    url="http://github.com/hedleyroos/cluster-sync",
    packages = find_packages(),
    dependency_links = [
    ],
    install_requires = [
        "inotify",
        "redis",
        "unhandled_exit"
    ],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
    ],
    zip_safe=False,
)
