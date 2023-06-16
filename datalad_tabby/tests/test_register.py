from datalad.tests.utils_pytest import assert_result_count


def test_register():
    import datalad.api as da
    assert hasattr(da, 'tabby_clone')
    assert_result_count(
        da.tabby_clone(on_failure='ignore'),
        1,
        action='tabby_clone')

