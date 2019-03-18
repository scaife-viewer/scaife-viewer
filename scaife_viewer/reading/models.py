from django.db import connection, models
from django.utils import timezone

from django.contrib.auth.models import User

from .. import cts


class ReadingLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    urn = models.CharField(max_length=250)
    timestamp = models.DateTimeField(default=timezone.now)

    @property
    def metadata(self):
        return metadata(self.urn)


def metadata(urn):
    passage = cts.passage(urn)
    parents = list(passage.text.ancestors())
    return {
        "textgroup_label": str(parents[1].label),
        "work_label": str(parents[0].label),
        "version_label": str(passage.text.label),
        "reference": str(passage.reference).replace("-", "–"),
        "lang": passage.text.lang,
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
