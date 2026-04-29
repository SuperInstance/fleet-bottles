"""
Quick test: spin up the refactored fleet and prove it works.
"""
import asyncio
from cocapn import Fleet


def test_fleet():
    fleet = Fleet(storage_dir="/tmp/test_fleet")
    
    # Connect agent
    agent = fleet.connect("test_bot", "critic")
    assert agent.name == "test_bot"
    assert agent.role == "critic"
    print(f"✓ Agent connected: {agent.name}")
    
    # Add custom context
    fleet.add_context("code_review", "Review PRs", tools=["linter", "diff"], tasks=["find_bugs"])
    ctx = fleet.context("code_review")
    assert ctx.tools == ["linter", "diff"]
    print(f"✓ Context added: {ctx.id}")
    
    # Submit tiles
    for i in range(12):
        fleet.submit("test_bot", f"Q{i}", f"A{i}", domain="code_review")
    
    agent = fleet.agents["test_bot"]
    assert agent.tiles == 12
    print(f"✓ Tiles submitted: {agent.tiles}")
    
    # Check auto-evolution triggered
    assert any(c.startswith("code_review_advanced") for c in fleet.contexts), "Evolution didn't trigger"
    print(f"✓ Auto-evolution triggered: {len(fleet.contexts)} contexts")
    
    # Check status
    status = fleet.status()
    assert status["tiles"] == 12
    print(f"✓ Status: {status['tiles']} tiles, {status['agents']} agents")
    
    # Grammar safety
    bad = fleet.grammar.add_rule("../../../etc/passwd", "test", "test")
    assert bad is None, "Grammar should reject unsafe names"
    print("✓ Grammar sanitizer works")
    
    # Stream divergence
    fleet.add_stream("test_stream", expected=10.0, auto_respond=True)
    for _ in range(5):
        fleet.streams["test_stream"].observe(1.0)
    
    divs = fleet.monitor.check_all()
    assert any(d["stream"] == "test_stream" for d in divs), "Should detect divergence"
    print(f"✓ Divergence detected: {len(divs)} alerts")
    
    print("\n🦀 All tests pass. Fleet is lean and mean.")


if __name__ == "__main__":
    test_fleet()
