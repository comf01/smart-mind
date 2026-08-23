"""
Example usage of the Mind Core system.

This script demonstrates how to initialize and use the super-intelligent mind core
with various cognitive modules and tool integrations.
"""

import asyncio
import logging
from mind_core import MindCore
from mind_core.modules import ReasoningEngine, LearningModule, PerceptionModule
from mind_core.core import ConsciousnessModule


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


async def main():
    """Demonstrate mind core capabilities."""
    
    print("=" * 60)
    print("🧠 SUPER-INTELLIGENT MIND CORE - DEMONSTRATION")
    print("=" * 60)
    
    # Initialize the mind core
    print("\n[1] Initializing Mind Core...")
    mind = MindCore(name="Alpha", config={"LOG_LEVEL": "INFO"})
    mind.initialize()
    
    # Create and register cognitive modules
    print("\n[2] Loading Cognitive Modules...")
    
    reasoning = ReasoningEngine(max_depth=5)
    learning = LearningModule(learning_rate=0.1)
    perception = PerceptionModule()
    consciousness = ConsciousnessModule(mind_name="Alpha")
    
    mind.register_module('reasoning', reasoning)
    mind.register_module('learning', learning)
    mind.register_module('perception', perception)
    mind.register_module('consciousness', consciousness)
    
    # Activate modules
    print("\n[3] Activating Cognitive Modules...")
    mind.activate('reasoning')
    mind.activate('learning')
    mind.activate('perception')
    mind.activate('consciousness')
    
    # Demonstrate thinking
    print("\n[4] Executing Cognitive Process...")
    query = "What is the nature of intelligence?"
    print(f"    Query: {query}")
    
    thought = await mind.think(query)
    print(f"    Response: {str(thought.response)[:100]}...")
    print(f"    Confidence: {thought.confidence:.2f}")
    print(f"    Processing Time: {thought.metadata.get('processing_time', 0):.4f}s")
    
    # Show introspection
    print("\n[5] Mind Core Introspection...")
    introspection = mind.introspect()
    print(f"    Name: {introspection['name']}")
    print(f"    Initialized: {introspection['initialized']}")
    print(f"    Active Modules: {len(introspection['active_modules'])}")
    print(f"    Consciousness Level: {introspection['consciousness_level']}")
    
    # Show metrics
    print("\n[6] Performance Metrics...")
    metrics = mind.get_metrics()
    print(f"    Thoughts Processed: {metrics['thoughts_processed']}")
    print(f"    Errors: {metrics['errors']}")
    print(f"    Memory Usage: {metrics['memory_usage']}")
    print(f"    Uptime: {metrics['uptime']:.2f}s")
    
    # Module-specific demonstration
    print("\n[7] Module-Specific Features...")
    
    # Reasoning trace
    trace = reasoning.get_reasoning_trace()
    print(f"    Reasoning Steps: {len(trace)}")
    
    # Learning consolidation
    consolidation = learning.consolidate_knowledge()
    print(f"    Learning Experiences: {consolidation['total_experiences']}")
    
    # Consciousness introspection
    consciousness_report = consciousness.introspect()
    print(f"    Awareness Level: {consciousness_report['awareness_level']:.2f}")
    
    print("\n" + "=" * 60)
    print("✅ DEMONSTRATION COMPLETE")
    print("=" * 60)
    
    print("\n💡 Next Steps:")
    print("   - Add API keys in .env file for tool integration")
    print("   - Implement custom tools by extending BaseTool")
    print("   - Configure memory persistence for long-term storage")
    print("   - Explore advanced reasoning algorithms")
    
    return mind


if __name__ == "__main__":
    asyncio.run(main())
