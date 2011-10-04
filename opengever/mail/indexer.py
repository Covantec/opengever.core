from DateTime import DateTime
from five import grok
from ftw.mail import utils
from ftw.mail.mail import IMail
from plone.indexer import indexer


@indexer(IMail)
def document_author(obj):
    """Return the sender address for the indexer document_author."""
    document_author = utils.get_header(obj.msg, 'From')
    document_author = document_author.replace('<', '&lt;')
    document_author = document_author.replace('>', '&gt;')
    return document_author
grok.global_adapter(document_author, name='document_author')


@indexer(IMail)
def document_date(obj):
    """Return the sent (not receipt) date of the mail for the
    document_date indexer.
    """
    document_date = utils.get_date_header(obj.msg, 'Date')
    return DateTime(document_date)
grok.global_adapter(document_date, name="document_date")


@indexer(IMail)
def receipt_date(obj):
    """Return the receipt date of the mail for the receipt_date indexer.
    We currently approximate this date by using the document date.
    """
    # TODO: Parse received-values of header mail
    document_date = utils.get_date_header(obj.msg, 'Date')
    return DateTime(document_date)
grok.global_adapter(receipt_date, name='receipt_date')


@indexer(IMail)
def sortable_author(obj):
    """Return the normalized author name for sortable_author indexer.
    For mails, this currently equals the document_author.
    """

    author = document_author(obj)()
    if author:
        return author.decode('utf8')
    else:
        return ''
grok.global_adapter(sortable_author, name='sortable_author')


@indexer(IMail)
def checked_out(obj):
    """Empty string checked out indexer, because we need an index value
    for sorted listings, but a mail can't be checked out so we return a
    empty string."""

    return ''
grok.global_adapter(checked_out, name='checked_out')
