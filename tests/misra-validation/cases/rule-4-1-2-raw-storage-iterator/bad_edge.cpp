// Edge cases: more forms of the violation.
#include <cstdint>
#include <memory>

namespace kv::rule_4_1_2_raw_storage_iterator::bad_edge {

bool same(const std::raw_storage_iterator<std::uint32_t*, std::uint32_t>& a) { return a.base() != nullptr; }

}  // namespace kv::rule_4_1_2_raw_storage_iterator::bad_edge
