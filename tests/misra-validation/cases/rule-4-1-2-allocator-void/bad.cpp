// Seeded violation: the deprecated std::allocator<void> specialisation.
#include <memory>

namespace kv::rule_4_1_2_allocator_void::bad {

using VoidAlloc = std::allocator<void>;

bool same(const VoidAlloc& a, const VoidAlloc& b) { return a == b; }

}  // namespace kv::rule_4_1_2_allocator_void::bad
