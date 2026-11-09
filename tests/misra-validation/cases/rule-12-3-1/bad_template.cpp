// Seeded violation (template): a union template.
#include <cstdint>

namespace kv::rule_12_3_1::bad_template {

template <typename T>
union Storage {  // seeded
  T value;
  std::uint8_t raw;
};

std::int32_t read(const Storage<std::int32_t>& s) { return s.value; }

}  // namespace kv::rule_12_3_1::bad_template
