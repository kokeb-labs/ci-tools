// Seeded violation: atoi called from a function template and from a lambda.
#include <cstdint>
#include <cstdlib>

namespace kv::rule_21_2_1::bad_template {

template <typename T>
T parse_as(const char* text) {
  return static_cast<T>(std::atoi(text));  // seeded
}

std::int32_t parse_both(const char* a, const char* b) {
  const auto via_lambda = [](const char* t) { return std::atoi(t); };  // seeded
  return parse_as<std::int32_t>(a) + via_lambda(b);
}

}  // namespace kv::rule_21_2_1::bad_template
