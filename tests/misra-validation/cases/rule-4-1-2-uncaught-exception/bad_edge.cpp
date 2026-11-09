// Edge cases: more forms of the violation.
#include <exception>

namespace kv::rule_4_1_2_uncaught_exception::bad_edge {

struct Guard {
  bool during_unwind{false};
  ~Guard() { during_unwind = std::uncaught_exception(); }  // seeded
};

}  // namespace kv::rule_4_1_2_uncaught_exception::bad_edge
