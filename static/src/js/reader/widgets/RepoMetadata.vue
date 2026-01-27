<template>
  <div class="repo-metadata-container">
    <LoaderBall v-if="$apollo.loading" />
    <EmptyMessage v-else-if="repos.length === 0"
      >No repository found</EmptyMessage
    >
    <template v-else>
      <div class="repo-name" v-if="gitHubUrl">
        <a v-if="gitHubUrl" class="value" :href="gitHubUrl" target="_blank">
          {{ repo.name }}
        </a>
      </div>
      <div class="repo-metadata-row">
        <div class="label">Release SHA:</div>
        <div class="value sha">
          <a :href="repoTreeUrl" target="_blank">
            {{ sha }}
          </a>
        </div>
      </div>
      <div class="report-issue-link">
        <a :href="newIssueUrl" target="_blank">
          Report an issue with this passage
        </a>
      </div>
    </template>
  </div>
</template>

<script>
// NOTE: (pletcher) This widget was originally provided by an external package at
// https://github.com/scaife-viewer/frontend/blob/main/packages/widget-repo-metadata/src/RepoMetadata.vue
// These packages are no longer being served correctly, so
// I'm inlining them here.
import gql from "graphql-tag";
import { LoaderBall, EmptyMessage } from "@scaife-viewer/common";

export default {
  name: "RepoMetadata",
  components: {
    LoaderBall,
    EmptyMessage,
  },
  props: ["passage"],
  computed: {
    repo() {
      return this.repos.slice(0, 1)[0];
    },
    gitHubUrl() {
      return this.repo.metadata.githubUrl;
    },
    sha() {
      return this.repo.sha.slice(0, 7);
    },
    ctsFilePath() {
      const [textGroup, workPart] = this.passage.work.split(".");
      return `data/${textGroup}/${workPart}/${this.passage.work}.xml`;
    },
    repoTreeUrl() {
      return `${this.gitHubUrl}/tree/${this.sha}/${this.ctsFilePath}`;
    },
    newIssueUrl() {
      const title = `Report an issue: ${this.passage}`;
      const body = `[${this.passage.work}.xml](${this.repoTreeUrl})`;
      return `${this.gitHubUrl}/issues/new?title=${title}&body=${body}`;
    },
  },
  apollo: {
    repos: {
      query: gql`
        query RepoMetadata($urn: String!) {
          versions(urn: $urn) {
            edges {
              node {
                repos {
                  edges {
                    node {
                      id
                      name
                      sha
                      metadata
                    }
                  }
                }
              }
            }
          }
        }
      `,
      variables() {
        return { urn: this.passage.version };
      },
      update(data) {
        return data.versions.edges
          .map((edge) => {
            return edge.node.repos.edges.map((repoEdge) => repoEdge.node);
          })
          .flat();
      },
      skip() {
        return !this.passage;
      },
    },
  },
};
</script>

<style lang="scss" scoped>
.repo-metadata-container {
  flex-direction: column;
  > * {
    font-size: 14px;
  }
  .github-logo {
    font-size: 12px;
  }
  .repo-metadata-row,
  .repo-name {
    > .label {
      color: var(--sv-widget-repo-metadata-label-text-color, #868e96);
    }
    > .value {
      margin-top: 0.25em;
      font-family: var(
        --sv-widget-repo-metadata-value-font-family,
        "Noto Serif"
      );
    }
    flex-flow: row nowrap;
    margin: 0.5em 0;
  }
  .sha > a {
    font-family: var(--sv-widget-repo-metadata-sha-font-family, monospace);
  }
  .report-issue-link {
    font-size: var(--sv-report-issue-link-font-size, 10px);
  }
}
</style>
