// Edge cases: more forms of the violation.
#include <cstdint>

namespace kv::rule_0_2_4::bad_edge {

namespace {
std::uint32_t helper(std::uint32_t v) { return v | 1U; }  // internal linkage, never called
}  // namespace

static std::uint32_t old_helper(std::uint32_t v) { return v; }  // internal linkage, never called

class Timer {
 public:
  std::uint32_t now() const { return ticks_; }

 private:
  static std::uint32_t scale(std::uint32_t v) { return v << 2U; }  // private static, never called
  std::uint32_t ticks_{0U};
};
std::uint32_t read(const Timer& t) { return t.now(); }

}  // namespace kv::rule_0_2_4::bad_edge
