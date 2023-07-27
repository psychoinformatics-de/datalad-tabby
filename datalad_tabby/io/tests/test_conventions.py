from .. import load_tabby


def test_load_tabby_scids(tmp_path):
    # minimalistic record in singledir format
    ds = tmp_path / 'dataset@tby-sd1.tsv'
    ds.write_text("name\tmyds\n")
    authors = tmp_path / 'authors@tby-sd1.tsv'
    authors.write_text(
        "name\temail\torcid\taffiliation\n"
        "Josiah Carberry\tjc@example.com\t0000-0002-1825-0097\tBrown University\n"
    )
    funding = tmp_path / 'funding@tby-sd1.tsv'
    funding.write_text(
        "funder\tgrant_id\ttitle\n"
        "DFG\tSFB000-INF\tShort but ambitious project\n"
    )
    loaded = load_tabby(ds, single=True, jsonld=True)
    # basic props
    assert loaded['name'] == 'myds'
    # context for everything
    for doc in (loaded, loaded['author'][0], loaded['funding'][0]):
        assert '@context' in doc
    # author @id
    assert all('@id' in a for a in loaded['author'])
    # and @types
    assert all('@type' in a for a in loaded['author'])
    assert all('@type' in f for f in loaded['funding'])
