// Seeded violation: the deprecated std::raw_storage_iterator.
#include <memory>
#include <cstdint>

namespace kv::rule_4_1_2_raw_storage_iterator::bad {

using It = std::raw_storage_iterator<std::uint32_t*, std::uint32_t>;  // seeded

It make(std::uint32_t* p) { return It(p); }

}  // namespace kv::rule_4_1_2_raw_storage_iterator::bad
