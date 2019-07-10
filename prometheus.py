import requests
from pathlib import Path
import datetime
from collections import namedtuple

# To get bearer token:
# Openshift-monitoring -> secrets -> prometheus-k8s-token-7qcrv (postfix might vary) -> token
bearer_token = 'Bearer ' + "eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJvcGVuc2hpZnQtbW9uaXRvcmluZyIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJwcm9tZXRoZXVzLWs4cy10b2tlbi03cWNydiIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50Lm5hbWUiOiJwcm9tZXRoZXVzLWs4cyIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6Ijc0MGQxZGViLWExOTQtMTFlOS05M2Y5LTBhYzFjMjdlMDI3NiIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpvcGVuc2hpZnQtbW9uaXRvcmluZzpwcm9tZXRoZXVzLWs4cyJ9.pzq9bRb0Q8GGwaAo7TVv2PKLDuzPd-KIYNkRvN_z75rYghfBsbqM_PkXM3ckRO7_hBWmFCTpRRHVkvldujXUlsxfn9KJz--_5k_8qSMy4h7aNAAaWeLMGdlJ7Zwsz0ecdg51TFuT9c32_t6dLiHFoWQaXDtRJWDVYwCtjqe7tUXMqu6jcnEprxWUXXilA-iy-5KNPKchBfWkNeFPfLkiKdtR1sEFLMvAVoxQDgYcyzeiiQVLb8RdHF5dutowKYFZl-BBWQzvueuNRgVSbVBqD0xTTwdSqKoMNrwpToKiSULf1FEHULHz0jiCE6RvYadrLHNdsoXhpB552kIDLAUNpQ"

# To get Cert file:
# Openshift-monitoring -> Secrets -> prometheus-k8s-tls.
# Copy 'tls.crt' into ~/.ssh/service.ca.crt -> chmod 600 service.ca.crt
cert_file = str(Path.home()) + "/.ssh/service.ca.crt"

# To find URL:
# Openshift-monitoring -> Stateful Sets -> Prometheus > copy external link + /api/v1/query
url = 'https://prometheus-k8s-openshift-monitoring.apps.toronto-5773.openshiftworkshop.com/api/v1/query'

# Query for prometheus.
# query = 'up' # for testing connectivity.
# query = "kube_pod_container_status_running{container='rest-service'}[2h]"
query = "kube_pod_container_status_ready{container='rest-service'}[3h]"

header = {'Authorization': bearer_token}
response = requests.post(url, headers=header, verify=cert_file, data={'query': query})
results = response.json()['data']['result']

pod_lifetimes = []   # Start/end epoch of each pod run.
for pod_samples in results:
    pod_started_epoch = pod_samples['values'][0][0]     # 0 = timestamp  1 = value.
    pod_terminated_epoch = pod_samples['values'][-1][0]
    pod_lifetimes.append((pod_started_epoch, pod_terminated_epoch))

if len(pod_lifetimes) == 0:
    print("No pods found")
    raise SystemExit

if len(pod_lifetimes) <= 1:
    print("Only a single Pod has been executing so far. Not enough to produce average downtime")
    raise SystemExit

# Workaround: Sort results manually by start/end dates.
# results are not sorted by start time. (Maybe they're sorted by pod name?)
# todo_someday - update prometheus query to sort by timestamp dates.
pod_lifetimes.sort(key=lambda x: x[0])

down_time_seconds = []
for i in range(0, len(pod_lifetimes)-1):
    pod_x_end = pod_lifetimes[i][1]
    pod_y_start = pod_lifetimes[i+1][0]
    offset_seconds = pod_y_start - pod_x_end
    down_time_seconds.append(offset_seconds)

average_seconds = sum(down_time_seconds) / len(down_time_seconds)

print("Total Downtime count: ", len(down_time_seconds))
print("Average duration Seconds:", average_seconds, "     (or in minutes: ", average_seconds/60,")")

# Sample 1:
# 1562778548 # 2019-07-10 13:09:08  pod_started
# 1562778788 # 2019-07-10 13:13:08  pod_terminated

# Sample 2:
# 1562779028 # 2019-07-10 13:17:08  pod_started
# 1562782028 # 2019-07-10 14:07:08  pod_terminated

# NOTES:

# Curl command to do a query on 'up'
# curl --cacert ~/.ssh/service.ca.crt -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJvcGVuc2hpZnQtbW9uaXRvcmluZyIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJwcm9tZXRoZXVzLWs4cy10b2tlbi03cWNydiIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50Lm5hbWUiOiJwcm9tZXRoZXVzLWs4cyIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6Ijc0MGQxZGViLWExOTQtMTFlOS05M2Y5LTBhYzFjMjdlMDI3NiIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpvcGVuc2hpZnQtbW9uaXRvcmluZzpwcm9tZXRoZXVzLWs4cyJ9.pzq9bRb0Q8GGwaAo7TVv2PKLDuzPd-KIYNkRvN_z75rYghfBsbqM_PkXM3ckRO7_hBWmFCTpRRHVkvldujXUlsxfn9KJz--_5k_8qSMy4h7aNAAaWeLMGdlJ7Zwsz0ecdg51TFuT9c32_t6dLiHFoWQaXDtRJWDVYwCtjqe7tUXMqu6jcnEprxWUXXilA-iy-5KNPKchBfWkNeFPfLkiKdtR1sEFLMvAVoxQDgYcyzeiiQVLb8RdHF5dutowKYFZl-BBWQzvueuNRgVSbVBqD0xTTwdSqKoMNrwpToKiSULf1FEHULHz0jiCE6RvYadrLHNdsoXhpB552kIDLAUNpQ" https://prometheus-k8s-openshift-monitoring.apps.toronto-5773.openshiftworkshop.com/api/v1/query?query=up

# GET call:
# url = 'https://prometheus-k8s-openshift-monitoring.apps.toronto-5773.openshiftworkshop.com/api/v1/query?query=up'
# r = requests.get(url, headers=header, verify=cert_file)


# from prometheus_client.parser import text_string_to_metric_families  # I think this is only for parsing /metrics