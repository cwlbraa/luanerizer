# luanerizer
putting the :luan: in :luan: since olden :luan:

## what is this?

This is a slack slash-command that inserts a :luan: emoji into the provided text
wherever it determines there's a noun lemma.

## why?

/luanerize In 2016, Cloudfoundry contributors started doing this organically out of respect for [luan](https://github.com/luan).

luanerizerAPP: In 2016, :luan: :luan:s started doing this organically out of :luan: for :luan:.

## how's that?

To accomplish this lofty goal it currently uses a lot of libraries and dev tools:
- [nltk](https://github.com/nltk/nltk) (for finding those noun lemmas)
- [python](https://github.com/python) (for nltk)
- [poetry](https://github.com/python-poetry/poetry) (for managing python
  libraries and venvs)
- [flask](https://github.com/pallets/flask) (for serving to Slack's POST request)
- [pre-commit](https://pre-commit.com/) so I don't forget to regenerate
  requirements.txt or format my code before committing.

[It's not a lot of python!](app.py)

Over the years I've carted this project around to various PaaSes as an exercise.

Today it leverages [knative](https://knative.dev/) as a unified, autoscaling
compute platform that can handle both synchronous http requests AND queued,
brokered, and asynchronous CloudEvents.

- Continuously builds and deploys with GCP's Cloud Build Service via [cloudbuild.yaml](cloudbuild.yaml)
- Uses [Heroku's Cloud Buildpacks](https://index.docker.io/r/heroku/buildpacks)
  to produce a ready-to-run container image from source
- GKE, Anthos, and Google Cloud Run to provide a knative runtime
- A Knative [Service](config/ksvc.yaml) as the only unit of compute
- A Knative [Broker](config/broker.yaml) & [Trigger](config/trigger.yaml) to
  queue and dispatch asynchronous requests
- [kapp](https://get-kapp.io/) & [ytt](https://get-ytt.io/) to wrangle k8s yamls and confirm successful rollouts

In the past, this was a 12-factor Cloudfoundry App. It ran on any CF, but mostly
lived on:
- [Pivotal Web Services](https://run.pivotal.io)
- [cf-for-k8s](https://github.com/cloudfoundry/cf-for-k8s)

It probably even still pushes, though anything asynchronous requires knative.
```bash
cf push luanerizer -b python_buildpack
```
