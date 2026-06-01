from __future__ import annotations

from example.communication_compiler.models import IdeaMap, IdeaMapEdge, IdeaMapNode, SessionState


def build_idea_map(session: SessionState) -> IdeaMap:
    nodes: list[IdeaMapNode] = []
    edges: list[IdeaMapEdge] = []
    if session.free_talk:
        nodes.append(
            IdeaMapNode(
                id="free_talk",
                type="user_input",
                label="Free Talk",
                text=session.free_talk[:280],
            )
        )
    selected = next((item for item in session.claim_candidates if item.claim_id == session.selected_claim_id), None)
    if selected:
        nodes.append(
            IdeaMapNode(id=selected.claim_id, type="claim_candidate", label="Selected Claim", text=selected.title)
        )
        if session.free_talk:
            edges.append(IdeaMapEdge(from_="free_talk", to=selected.claim_id, type="derived_from"))
    if session.current_message_kernel is None:
        return IdeaMap(nodes=nodes, edges=edges)

    kernel = session.current_message_kernel
    kernel_nodes = [
        ("premise", "Audience Premise", kernel.premise),
        ("complication", "Complication", kernel.complication),
        ("claim", "Core Claim", kernel.claim),
        ("action", "Requested Action", kernel.action),
    ]
    for node_id, label, text in kernel_nodes:
        nodes.append(IdeaMapNode(id=node_id, type="kernel_line", label=label, text=text))
    edges.extend(
        [
            IdeaMapEdge(from_="premise", to="complication", type="leads_to"),
            IdeaMapEdge(from_="complication", to="claim", type="supports"),
            IdeaMapEdge(from_="claim", to="action", type="requires_decision"),
        ]
    )
    if selected:
        edges.append(IdeaMapEdge(from_=selected.claim_id, to="claim", type="refines"))

    for item in session.supporting_evidence:
        nodes.append(IdeaMapNode(id=item.evidence_id, type="evidence", label=item.title, text=item.summary))
        edges.append(IdeaMapEdge(from_=item.evidence_id, to=item.supports_kernel_line, type="supports"))
    for item in session.evidence_gaps:
        nodes.append(IdeaMapNode(id=item.gap_id, type="gap", label="Evidence Gap", text=item.description))
        edges.append(IdeaMapEdge(from_=item.gap_id, to="action", type="weakens"))
    for item in session.objections:
        nodes.append(IdeaMapNode(id=item.objection_id, type="objection", label="Objection", text=item.objection))
        edges.append(IdeaMapEdge(from_=item.objection_id, to="claim", type="challenges"))

    return IdeaMap(nodes=nodes, edges=edges)
