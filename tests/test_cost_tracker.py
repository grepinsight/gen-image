"""Tests for cost tracking."""

from gen_image.cost_tracker import CostTracker


class TestCostTracker:
    def test_empty_history(self, tmp_history):
        tracker = CostTracker(history_file=tmp_history)
        assert tracker.get_history() == []

    def test_log_and_retrieve(self, tmp_history):
        tracker = CostTracker(history_file=tmp_history)
        tracker.log_generation(
            prompt="test prompt",
            output_path="/tmp/test.png",
            cost=0.04,
            provider="openai",
            model="gpt-image-2",
        )
        entries = tracker.get_history()
        assert len(entries) == 1
        assert entries[0]["prompt"] == "test prompt"
        assert entries[0]["cost"] == 0.04
        assert entries[0]["provider"] == "openai"

    def test_history_most_recent_first(self, tmp_history):
        tracker = CostTracker(history_file=tmp_history)
        tracker.log_generation(prompt="first", output_path="/a.png", cost=0.01)
        tracker.log_generation(prompt="second", output_path="/b.png", cost=0.02)
        entries = tracker.get_history()
        assert entries[0]["prompt"] == "second"

    def test_history_limit(self, tmp_history):
        tracker = CostTracker(history_file=tmp_history)
        for i in range(5):
            tracker.log_generation(prompt=f"p{i}", output_path=f"/{i}.png", cost=0.01)
        entries = tracker.get_history(limit=2)
        assert len(entries) == 2

    def test_history_search(self, tmp_history):
        tracker = CostTracker(history_file=tmp_history)
        tracker.log_generation(prompt="red fox", output_path="/fox.png", cost=0.04)
        tracker.log_generation(prompt="blue bird", output_path="/bird.png", cost=0.04)
        entries = tracker.get_history(search="fox")
        assert len(entries) == 1
        assert "fox" in entries[0]["prompt"]

    def test_stats_empty(self, tmp_history):
        tracker = CostTracker(history_file=tmp_history)
        stats = tracker.get_stats()
        assert stats["total_generations"] == 0
        assert stats["total_cost"] == 0.0

    def test_stats_with_entries(self, tmp_history):
        tracker = CostTracker(history_file=tmp_history)
        tracker.log_generation(prompt="a", output_path="/a.png", cost=0.04)
        tracker.log_generation(prompt="b", output_path="/b.png", cost=0.08)
        stats = tracker.get_stats()
        assert stats["total_generations"] == 2
        assert stats["total_cost"] == 0.12

    def test_clear_history(self, tmp_history):
        tracker = CostTracker(history_file=tmp_history)
        tracker.log_generation(prompt="a", output_path="/a.png", cost=0.04)
        tracker.clear_history()
        assert tracker.get_history() == []
