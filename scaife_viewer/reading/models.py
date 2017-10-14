from django.db import connection, models
from django.utils import timezone

from django.contrib.auth.models import User

from ..cts import CTS


class ReadingLog(models.Model):
    user = models.ForeignKey(User)
    urn = models.CharField(max_length=250)
    timestamp = models.DateTimeField(default=timezone.now)

    @property
    def metadata(self):
        return metadata(self.urn)


def metadata(urn):
    cts = CTS()
    passage = cts.passage(urn)
    parents = passage.metadata.parents
    return {
        "textgroup_label": str(parents[1].get_label()),
        "work_label": str(parents[0].get_label()),
        "version_label": str(passage.metadata.get_label()),
        "reference": str(passage.reference),
        "lang": passage.lang,
    }


def recent(user, limit=5):
    with connection.cursor() as cursor:
        sql = "SELECT urn, MAX(timestamp) AS timestamp FROM reading_readinglog WHERE user_id = %s GROUP BY urn ORDER BY timestamp DESC LIMIT %s"
        cursor.execute(sql, [user.pk, limit])

        return [
            {
                "metadata": metadata(row[0]),
                "urn": row[0],
                "timestamp": row[1],
            }
            for row in cursor.fetchall()
        ]
