// Seeded violation: the C++17-deprecated member typedef std::allocator<T>::reference. C++20 removes it, so this
// file does not compile in the project's language mode: the guideline is not exercisable there.
#include <cstdint>
#include <memory>

namespace kv::rule_4_1_2_allocator_member::bad {

using Alloc = std::allocator<std::uint32_t>;
using Ref = Alloc::reference;  // seeded

Ref first(Ref r) { return r; }

}  // namespace kv::rule_4_1_2_allocator_member::bad
