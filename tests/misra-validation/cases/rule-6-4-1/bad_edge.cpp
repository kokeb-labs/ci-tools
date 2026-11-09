// Edge cases: more forms of the violation.
#include <cstdint>

namespace kv::rule_6_4_1::bad_edge {

class Gauge {
 public:
  std::int32_t read() const {
    std::int32_t level = 0;  // seeded
    return level;
  }

 private:
  std::int32_t level{3};
};

std::int32_t clip(std::int32_t limit) {
  std::int32_t out = 0;
  if (limit > 0) {
    std::int32_t limit = 1;  // seeded
    out = limit;
  }
  return out;
}

std::int32_t g_scale = 2;

std::int32_t scaled(std::int32_t v) {
  std::int32_t g_scale = v;  // seeded
  return g_scale;
}

std::int32_t via_lambda(std::int32_t v) {
  const auto f = [v]() {
    std::int32_t v = 1;  // seeded
    return v;
  };
  return f();
}

}  // namespace kv::rule_6_4_1::bad_edge
