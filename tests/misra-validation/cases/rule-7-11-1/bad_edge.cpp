// Edge cases of the seeded violation.
#include <cstddef>
#include <cstdint>

namespace kv::rule_7_11_1::bad_edge {

std::int32_t const* none() { return 0; }

bool is_set(std::int32_t const* p) { return p != 0; }

std::int32_t read(std::int32_t const* p) { return (p == nullptr) ? 0 : *p; }

std::int32_t read_null() { return read(NULL); }

}  // namespace kv::rule_7_11_1::bad_edge
