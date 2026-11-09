// Seeded violation (typedef): a third level of pointer hidden behind an alias.
#include <cstdint>

namespace kv::rule_11_3_2::bad_typedef {

using IntPtr = std::int32_t*;

std::int32_t deref3(IntPtr* const* p) { return ***p; }  // seeded

}  // namespace kv::rule_11_3_2::bad_typedef
