import prefect

from prefect.executors import dask

from prefectflows import flow, kubernetes, azure


PREFECT_FLOWS_STORAGE_CONNECTION_SECRET = "STORAGE_BACKEND_CONN_STRING"


class Update(kubernetes.KubernetesTask):
    def __init__(self, cpus: int, memory: int, **kwargs):
        super().__init__(
            image="dhidna.azurecr.io/scatterometry-downloader:v0.0.1",
            cpus=cpus,
            memory=memory,
            **kwargs,
        )

    def run(
        self,
        database_url,
        earthdata_username,
        earthdata_password,
        mode,
        collections,
        start_timestamp,
        end_timestamp,
        bbox,
        provider
    ):

        command_line_arguments = [
            f"--mode {mode}",
            f"--collections-shortnames {collections}",
            f"--start-date {start_timestamp}" if start_timestamp else "",
            f"--end-date {end_timestamp}" if end_timestamp else "",
            f"--bounds {bbox}" if bbox else "",
            f"--provider {provider}" if provider else "",
        ]

        self.run_gem(
            args=command_line_arguments,
            env={
                "DATABASE_URL": database_url,
                "EARTHDATA_USERNAME": earthdata_username,
                "EARTHDATA_PASSWORD": earthdata_password,
            },
        )

        return


if __name__ == "__main__":
    project_name = "scatterometry"
    flow_name = "updater"
    with flow.standard_flow(
        flow_name=flow_name,
        azure_connection_secret=PREFECT_FLOWS_STORAGE_CONNECTION_SECRET,
        memory_request="1Gi",
        cpu_request="1",
        image_and_tag="prefect-scatterometry-updater:v0.0.1",
        exclusive=True,
    ) as current_flow:

        database_url = azure.Secret("scatterometry-database-url")
        earthdata_username = azure.Secret("scatterometry-earthdata-username")
        earthdata_password = azure.Secret("scatterometry-earthdata-password")

        mode = prefect.Parameter("mode", default="update")
        collections = prefect.Parameter("collections-shortnames", default="ASCATA-L2-Coastal,ASCATA_L2_COASTAL_CDR,ASCATB-L2-Coastal,ASCATC-L2-Coastal,CYGNSS_L2_V3.1,OS2_OSCAT_LEVEL_2B_OWV_COMP_12_V2,QSCAT_LEVEL_2B_OWV_COMP_12_KUSST_LCRES_4.1,RSCAT_LEVEL_2B_OWV_CLIM_12_V2")
        start_timestamp = prefect.Parameter("start-timestamp", default=None)
        end_timestamp = prefect.Parameter("end-timestamp", default=None)
        bbox = prefect.Parameter("bbox", default=None)
        provider = prefect.Parameter("provider", default=None)

        update = Update(cpus=1, memory=1, task_run_name="Update")

        update(
            database_url=database_url,
            earthdata_username=earthdata_username,
            earthdata_password=earthdata_password,
            mode=mode,
            collections=collections,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            bbox=bbox,
            provider=provider
        )

    current_flow.executor = dask.LocalDaskExecutor(num_workers=300)
    current_flow.register(project_name=project_name)
