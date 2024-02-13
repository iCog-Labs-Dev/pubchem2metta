"""
Knowledge graph generation through BioCypher script
"""
from adapters.has_same_connectivity_adapter import HasSameConnectivityAsEdge
from metta_writer import *
from biocypher._logger import logger
from adapters.compound_adapter import CompoundAdapter
from adapters.has_component_adapter import HasComponentEdge

ADAPTERS = {
    # "compound": {
    #     "adapter": CompoundAdapter(
    #         filepath="samples/pc_compound2descriptor_000001_chunk_1.xml", dry_run=True
    #     ),
    #     "outdir": "compound_complexity",
    #     "nodes": True,
    #     "edges": False,
    # },
    # "compound2component": {
    #     "adapter": HasComponentEdge(
    #         filepath="samples/pc_compound2component.xml", dry_run=False
    #     ),
    #     "outdir": "compound2component",
    #     "nodes": False,
    #     "edges": True
    # },
    "hasSameConnectivityAs": {
        "adapter": HasSameConnectivityAsEdge(
            filepath="samples/pc_compound2sameconnectivity.xml", dry_run=False
        ),
        "outdir": "compound2sameconnectivity",
        "nodes": False,
        "edges": True
    }  
}


# Run build
def main():
    """
    Main function. Call individual adapters to download and process data. Build
    via BioCypher from node and edge data.
    """

    # Start biocypher

    bc = MeTTaWriter(
        schema_config="config/schema_config.yaml",
        biocypher_config="config/biocypher_config.yaml",
        output_dir="metta_out",
    )

    # Run adapters

    for k, v in ADAPTERS.items():
        logger.info("Running adapter: " + k)
        adapter = v["adapter"]
        write_nodes = v["nodes"]
        write_edges = v["edges"]
        outdir = v["outdir"]

        if write_nodes:
            nodes = adapter.get_nodes()
            bc.write_nodes(nodes, path_prefix=outdir)

        if write_edges:
            edges = adapter.get_edges()
            bc.write_edges(edges, path_prefix=outdir)

    logger.info("Done")


if __name__ == "__main__":
    main()
