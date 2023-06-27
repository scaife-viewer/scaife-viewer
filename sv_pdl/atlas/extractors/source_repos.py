from scaife_viewer.atlas.models import Repo


def set_upstream_repo_names():
    to_update = []
    for repo in Repo.objects.all():
        parts = repo.metadata["github_url"].rsplit("/", maxsplit=2)[1:]
        source_repo_name = "/".join(parts)
        repo.name = source_repo_name
        to_update.append(repo)
    Repo.objects.bulk_update(to_update, fields=["name"])
