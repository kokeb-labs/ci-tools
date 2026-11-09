// Seeded violation: a member typedef of std::allocator listed by the query (the C++17-deprecated ones are removed in C++20 libraries).
#include <memory>
#include <cstdint>

namespace kv::rule_4_1_2_allocator_member::bad {

using Alloc = std::allocator<std::uint32_t>;
using Ref = Alloc::value_type&;

Ref first(Ref r) { return r; }

}  // namespace kv::rule_4_1_2_allocator_member::bad
