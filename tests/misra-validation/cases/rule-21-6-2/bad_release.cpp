// Seeded violation: ownership taken out of a unique_ptr and deleted by hand.
#include <cstdint>
#include <memory>

namespace kv::rule_21_6_2::bad_release {

std::int32_t drain(std::unique_ptr<std::int32_t> owner) {
  std::int32_t* raw = owner.release();  // seeded
  const std::int32_t value = *raw;
  delete raw;  // seeded
  return value;
}

}  // namespace kv::rule_21_6_2::bad_release
