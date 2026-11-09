// Seeded violation: the results of remove_if, unique_ptr::release and std::array::empty thrown away.
#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>

namespace kv::rule_28_6_4::bad_more {

void drop_negatives(std::array<std::int32_t, 4U>& values) {
  std::remove_if(values.begin(), values.end(), [](std::int32_t v) { return v < 0; });
}

void forget(std::unique_ptr<std::int32_t>& owner) { owner.release(); }

void probe(const std::array<std::int32_t, 4U>& values) { values.empty(); }

}  // namespace kv::rule_28_6_4::bad_more
