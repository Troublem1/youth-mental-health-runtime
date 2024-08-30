import importlib
import subprocess

import pytest

packages = [
    "numpy",
    "pandas",
    "scipy",
    "spacy",
    "sklearn",
    "torch",
    "transformers",
]


def is_gpu_available():
    try:
        return subprocess.check_call(["nvidia-smi"]) == 0

    except FileNotFoundError:
        return False


GPU_AVAILABLE = is_gpu_available()


@pytest.mark.parametrize("package_name", packages, ids=packages)
def test_import(package_name):
    """Test that certain dependencies are importable."""
    importlib.import_module(package_name)


@pytest.mark.skipif(not GPU_AVAILABLE, reason="No GPU available")
def test_allocate_torch():
    import torch

    assert torch.cuda.is_available()

    torch.zeros(1).cuda()


@pytest.mark.skipif(not GPU_AVAILABLE, reason="No GPU available")
def test_allocate_cupy():
    import cupy as cp

    cp.array([1, 2, 3, 4, 5, 6])


@pytest.mark.skipif(not GPU_AVAILABLE, reason="No GPU available")
def test_bitsandbytes_available():
    from transformers.utils import is_bitsandbytes_available

    assert is_bitsandbytes_available()


def test_spacy():
    import spacy
    from spacy.tokens import DocBin

    if GPU_AVAILABLE:
        spacy.require_gpu()

    nlp = spacy.blank("en")
    training_data = [
        ("Tokyo Tower is 333m tall.", [(0, 11, "BUILDING")]),
    ]

    # the DocBin will store the example documents
    db = DocBin()
    for text, annotations in training_data:
        doc = nlp(text)
        ents = []
        for start, end, label in annotations:
            span = doc.char_span(start, end, label=label)
            ents.append(span)
        doc.ents = ents
        db.add(doc)
