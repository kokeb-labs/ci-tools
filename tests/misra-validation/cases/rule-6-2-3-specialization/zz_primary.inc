// The primary template, in its own file.
#include <cstdint>

namespace kv::rule_6_2_3_specialization::bad {

template <typename T>
struct Width {
  static constexpr std::int32_t kBits{0};
};

}  // namespace kv::rule_6_2_3_specialization::bad
